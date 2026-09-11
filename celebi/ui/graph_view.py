"""Graph visualization — card-based layout with prompt/response pairs."""

import json
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsItem, QGraphicsPolygonItem,
    QGraphicsPathItem,
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel,
    QGraphicsSimpleTextItem,
)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QPen, QBrush, QColor, QFont, QPainter, QPainterPath,
    QPolygonF,
)


PROMPT_BG = QColor("#1a3a4a")
RESPONSE_BG = QColor("#1a3a2a")
PROMPT_BORDER = QColor("#4FC3F7")
RESPONSE_BORDER = QColor("#81C784")
HIGHLIGHT_BORDER = QColor("#FFC107")
EDGE_COLOR = QColor("#555")
TEXT_COLOR = QColor("#d4d4d4")
DIM_TEXT = QColor("#888")


class ConversationCard(QGraphicsRectItem):
    CARD_W = 280
    CARD_H = 100

    def __init__(self, node_id, step_type, payload, x, y):
        super().__init__(0, 0, self.CARD_W, self.CARD_H)
        self.node_id = node_id
        self.step_type = step_type
        self.payload = payload
        self._is_highlighted = False

        self.setPos(x, y)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)

        bg = PROMPT_BG if step_type == "prompt" else RESPONSE_BG
        border = PROMPT_BORDER if step_type == "prompt" else RESPONSE_BORDER
        self._default_border = border
        self.setBrush(QBrush(bg))
        self.setPen(QPen(border, 2))

        # Type label — using QGraphicsSimpleTextItem for reliable rendering
        type_label = QGraphicsSimpleTextItem(step_type.upper(), self)
        type_label.setBrush(QBrush(border))
        type_label.setFont(QFont("Sans", 8, QFont.Weight.Bold))
        type_label.setPos(10, 6)

        # ID label
        id_label = QGraphicsSimpleTextItem(node_id[:8], self)
        id_label.setBrush(QBrush(DIM_TEXT))
        id_label.setFont(QFont("Monospace", 7))
        id_label.setPos(self.CARD_W - 65, 8)

        # Content preview — truncated to fit card
        preview = self._get_text_preview()
        # Split into lines that fit the card width (~35 chars per line)
        max_chars = 35
        lines = []
        while preview and len(lines) < 3:
            if len(preview) <= max_chars:
                lines.append(preview)
                break
            # Find a good break point
            cut = preview[:max_chars].rfind(" ")
            if cut < 10:
                cut = max_chars
            lines.append(preview[:cut] + "...")
            preview = preview[cut:].lstrip()

        for j, line in enumerate(lines):
            item = QGraphicsSimpleTextItem(line, self)
            item.setBrush(QBrush(TEXT_COLOR))
            item.setFont(QFont("Sans", 9))
            item.setPos(10, 30 + j * 16)

    def _get_text_preview(self) -> str:
        if self.step_type == "prompt":
            try:
                data = json.loads(self.payload)
                msgs = data.get("messages", [])
                # Get the LAST user message (the actual new request)
                for m in reversed(msgs):
                    if m.get("role") == "user":
                        text = m.get("content", "")
                        text = text.replace("\n", " ").strip()
                        return text[:70] + "..." if len(text) > 70 else text
                return "(no user message)"
            except:
                return self.payload[:70]
        else:
            parts = []
            for c in self.payload.split("data: "):
                c = c.strip()
                if not c or c == "[DONE]":
                    continue
                try:
                    d = json.loads(c)
                    content = d.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if content:
                        parts.append(content)
                except:
                    pass
            full = "".join(parts).replace("\n", " ").strip()
            if full:
                return full[:70] + "..." if len(full) > 70 else full
            return "(no response)"

    def highlight(self, on=True):
        self._is_highlighted = on
        border = HIGHLIGHT_BORDER if on else self._default_border
        width = 3 if on else 2
        self.setPen(QPen(border, width))

    def hoverEnterEvent(self, event):
        if not self._is_highlighted:
            self.setPen(QPen(QColor("#fff"), 2))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        border = HIGHLIGHT_BORDER if self._is_highlighted else self._default_border
        width = 3 if self._is_highlighted else 2
        self.setPen(QPen(border, width))
        super().hoverLeaveEvent(event)


class ConversationArrow(QGraphicsPathItem):
    def __init__(self, src_card, tgt_card):
        super().__init__()
        src_y = src_card.pos().y() + ConversationCard.CARD_H / 2
        tgt_y = tgt_card.pos().y() + ConversationCard.CARD_H / 2
        src_x = src_card.pos().x() + ConversationCard.CARD_W
        tgt_x = tgt_card.pos().x()

        p0 = QPointF(src_x, src_y)
        p3 = QPointF(tgt_x, tgt_y)
        mid_x = (src_x + tgt_x) / 2

        path = QPainterPath()
        path.moveTo(p0)
        path.cubicTo(QPointF(mid_x, src_y), QPointF(mid_x, tgt_y), p3)

        self.setPath(path)
        self.setPen(QPen(EDGE_COLOR, 2))
        self.setZValue(0)

        # Arrowhead
        arrow_size = 8
        angle = 0.4
        dx = p3.x() - mid_x
        dy = p3.y() - mid_x
        length = max((dx**2 + dy**2) ** 0.5, 1)
        ux, uy = dx / length, dy / length

        left = QPointF(
            p3.x() - arrow_size * (ux + uy * angle),
            p3.y() - arrow_size * (uy - ux * angle),
        )
        right = QPointF(
            p3.x() - arrow_size * (ux - uy * angle),
            p3.y() - arrow_size * (uy + ux * angle),
        )
        self._arrow = QPolygonF([p3, left, right])

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        painter.setBrush(QBrush(EDGE_COLOR))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(self._arrow)


class NodeDetailDialog(QDialog):
    def __init__(self, node_id, step_type, payload, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{step_type.upper()} — {node_id[:12]}..")
        self.setMinimumSize(600, 450)

        layout = QVBoxLayout(self)

        header = QLabel(f"<b>{step_type.upper()}</b> — {node_id}")
        header.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(header)

        if step_type == "prompt":
            display_text = self._format_prompt(payload)
        else:
            display_text, tokens = self._format_response(payload)
            if tokens:
                t = QLabel(f"Tokens: {tokens}")
                t.setStyleSheet("color: #888; font-size: 11px;")
                layout.addWidget(t)

        text_edit = QTextEdit()
        text_edit.setPlainText(display_text)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Monospace", 11))
        text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        text_edit.setStyleSheet(
            "QTextEdit { background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #444; padding: 8px; }"
        )
        layout.addWidget(text_edit)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def _format_prompt(self, payload):
        """Extract only the last user message."""
        try:
            data = json.loads(payload)
            messages = data.get("messages", [])
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    return msg.get("content", "")
            return "(no user message)"
        except:
            return payload

    def _format_response(self, payload):
        parts = []
        tokens = None
        for c in payload.split("data: "):
            c = c.strip()
            if not c or c == "[DONE]":
                continue
            try:
                d = json.loads(c)
                content = d.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if content:
                    parts.append(content)
                usage = d.get("usage")
                if usage:
                    pt = usage.get("prompt_tokens", 0)
                    ct = usage.get("completion_tokens", 0)
                    tokens = f"{pt} prompt + {ct} completion = {pt + ct} total"
            except:
                pass
        return "".join(parts) or "(no text)", tokens


class GraphView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def clear(self):
        self._scene.clear()

    def load_graph(self, edges: list, proxy_port: int):
        self.clear()
        if not edges:
            return

        card_w = ConversationCard.CARD_W
        card_h = ConversationCard.CARD_H
        gap = 60
        row_gap = 30

        last_prompt = None
        last_response = None

        for i, e in enumerate(edges):
            y = i * (card_h + row_gap)

            prompt_card = ConversationCard(
                e["source_id"], "prompt", e.get("source_payload", ""), 0, y
            )
            self._scene.addItem(prompt_card)

            resp_card = ConversationCard(
                e["target_id"], "response", e.get("target_payload", ""),
                card_w + gap, y,
            )
            self._scene.addItem(resp_card)

            arrow = ConversationArrow(prompt_card, resp_card)
            self._scene.addItem(arrow)

            last_prompt = prompt_card
            last_response = resp_card

        # Highlight last conversation
        if last_prompt:
            last_prompt.highlight(True)
        if last_response:
            last_response.highlight(True)

        # Fit all cards in view
        self.fitInView(
            self._scene.sceneRect().adjusted(-40, -40, 40, 40),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def mousePressEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        if isinstance(item, ConversationCard):
            dialog = NodeDetailDialog(
                item.node_id, item.step_type, item.payload, self.window()
            )
            dialog.exec()
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        self.scale(factor, factor)
