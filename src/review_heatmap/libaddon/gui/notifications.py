# -*- coding: utf-8 -*-

# Libaddon for Anki
#
# Copyright (C) 2018-2021  Aristotelis P. <https//glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Customizable notification pop-up
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, Optional, Type

from aqt.qt import (
    QEvent,
    QObject,
    QPoint,
    Qt,
    QTimer,
    pyqtSignal,
    QCloseEvent,
    QColor,
    QMouseEvent,
    QPalette,
    QResizeEvent,
    QApplication,
    QFrame,
    QLabel,
    QWidget,
    QCursor,
)

if TYPE_CHECKING:
    from aqt import AnkiApp
    from aqt.progress import ProgressManager


class NotificationHAlignment(Enum):
    left = "left"
    center = "center"
    right = "right"


class NotificationVAlignment(Enum):
    top = "top"
    center = "center"
    bottom = "bottom"


class FocusBehavior(Enum):
    always_on_top = "always_on_top"
    close_on_window_focus_lost = "close_on_window_focus_lost"
    lower_on_window_focus_lost = "lower_on_window_focus_lost"
    close_on_application_focus_lost = "close_on_application_focus_lost"


@dataclass
class NotificationSettings:
    """Notification settings

    Args:
        duration: Time in ms the notification should be shown for. Set to None or 0
            for a persistent tooltip that has to be dismissed manually
        focus_behavior_exceptions: Only relevant when focus behavior is not set to
            FocusBehavior.always_on_top.
            List of window classes for which the focus behavior set does not apply,
            i.e. for which the notification stays visible and on top of even if the
            window focus changes.

    """

    duration: Optional[int] = 3000
    align_horizontal: NotificationHAlignment = NotificationHAlignment.left
    align_vertical: NotificationVAlignment = NotificationVAlignment.bottom
    space_horizontal: int = 0
    space_vertical: int = 0
    fg_color: str = "#000000"
    bg_color: str = "#FFFFFF"
    dismiss_on_click: bool = True
    focus_behavior: FocusBehavior = FocusBehavior.always_on_top
    focus_behavior_exceptions: Optional[List[Type[QWidget]]] = None


class NotificationEventFilter(QObject):
    def __init__(self, notification: "Notification"):
        super().__init__(parent=notification)
        self._notification = notification

    def eventFilter(self, object: QObject, event: QEvent) -> bool:
        event_type = event.type()
        if event_type == QEvent.Type.Resize or event_type == QEvent.Type.Move:
            self._notification.update_position()
            self._notification.show()  # needed on macOS

        return super().eventFilter(object, event)


class NotificationService(QObject):
    def __init__(
        self,
        progress_manager: "ProgressManager",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent=parent)
        self._parent = parent
        self._progress_manager = progress_manager

        self._current_timer: Optional[QTimer] = None
        self._current_instance: Optional["Notification"] = None
        self._current_event_filter: Optional[NotificationEventFilter] = None

    def notify(
        self,
        message: str,
        settings: NotificationSettings,
        link_handler: Optional[Callable[[str], None]] = None,
        pre_show_callback: Optional[Callable[["Notification"], None]] = None,
    ):
        self.close_current_notification()

        notification = Notification(
            text=message, settings=settings, parent=self._parent
        )
        if link_handler:
            notification.setOpenExternalLinks(False)
            notification.linkActivated.connect(link_handler)

        if self._parent:
            self._current_event_filter = NotificationEventFilter(
                notification=notification
            )
            self._parent.installEventFilter(self._current_event_filter)

        if pre_show_callback:
            pre_show_callback(notification)

        notification.show()

        self._current_instance = notification

        if settings.duration:
            self._current_timer = self._progress_manager.timer(
                3000, self.close_current_notification, False
            )

        notification.closed.connect(self.close_current_notification)

    def close_current_notification(self):
        if self._current_instance:
            try:
                self._current_instance.deleteLater()
            except Exception:
                # already deleted as parent window closed
                pass
            self._current_instance = None
        if self._current_event_filter:
            try:
                if self._parent:
                    self._parent.removeEventFilter(self._current_event_filter)
                self._current_event_filter.deleteLater()
            except Exception:
                # already deleted as parent window closed
                pass
            self._current_event_filter = None
        if self._current_timer:
            self._current_timer.stop()
            self._current_timer = None


class Notification(QLabel):

    # Anki dialog manager support
    silentlyClose = True

    closed = pyqtSignal()

    def __init__(
        self,
        text: str,
        settings: NotificationSettings = NotificationSettings(),
        parent: Optional[QWidget] = None,
        **kwargs,
    ):
        super().__init__(text, parent=parent, **kwargs)
        self._settings = settings

        self.setFrameStyle(QFrame.Shape.Panel)
        self.setLineWidth(2)
        self.setWindowFlags(Qt.WindowType.ToolTip)
        self.setContentsMargins(10, 10, 10, 10)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self._settings.bg_color))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(self._settings.fg_color))
        self.setPalette(palette)

        if parent and self._settings.focus_behavior != FocusBehavior.always_on_top:
            app: "AnkiApp" = QApplication.instance()  # type: ignore[assignment]
            app.focusChanged.connect(self._on_app_focus_changed)

    def _on_app_focus_changed(
        self, old_widget: Optional[QWidget], new_widget: Optional[QWidget]
    ):
        focus_behavior = self._settings.focus_behavior
        focus_exceptions = self._settings.focus_behavior_exceptions
        parent_window = self.parent().window()
        old_window = old_widget.window() if old_widget else None
        new_window = new_widget.window() if new_widget else None

        if focus_exceptions and any(
            isinstance(old_window, wtype) for wtype in focus_exceptions
        ):
            # switching back from an excluded window should not cause notif closing
            pass
        elif new_window is None and QApplication.widgetAt(QCursor.pos()) == self:
            # clicking on self should not dismiss notification when not configured as
            # such (Windows bug)
            pass
        elif new_window is None:
            # switched focus away from application
            self.close()
        elif new_window != parent_window and (
            not focus_exceptions
            or (all(not isinstance(new_window, wtype) for wtype in focus_exceptions))
        ):
            # switched to other window within same application that's not excluded
            if focus_behavior == FocusBehavior.close_on_window_focus_lost:
                self.close()
            elif focus_behavior == FocusBehavior.lower_on_window_focus_lost:
                self.setWindowFlag(Qt.WindowType.ToolTip, on=False)
        elif (
            new_window == parent_window
            and focus_behavior == FocusBehavior.lower_on_window_focus_lost
        ):
            self.setWindowFlag(Qt.WindowType.ToolTip, on=True)
            self.show()

    def mousePressEvent(self, event: QMouseEvent):
        if (
            not self._settings.dismiss_on_click
            or self.cursor().shape() == Qt.CursorShape.PointingHandCursor
        ):
            # Do not ignore mouse press event if configured that way and/or
            # currently hovering link (as signaled by cursor shape)
            return super().mousePressEvent(event)
        event.accept()
        self.close()

    def closeEvent(self, event: QCloseEvent):
        self.closed.emit()
        return super().closeEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        # true geometry is only known once resizeEvent fires
        self.update_position()
        super().resizeEvent(event)

    def update_position(self):
        align_horizontal = self._settings.align_horizontal
        align_vertical = self._settings.align_vertical

        if align_horizontal == NotificationHAlignment.left:
            x = 0 + self._settings.space_horizontal
        elif align_horizontal == NotificationHAlignment.right:
            x = self.parent().width() - self.width() - self._settings.space_horizontal
        elif align_horizontal == NotificationHAlignment.center:
            x = (self.parent().width() - self.width()) / 2
        else:
            raise ValueError(f"Alignment value {align_horizontal} is not supported")

        if align_vertical == NotificationVAlignment.top:
            y = 0 + self._settings.space_vertical
        elif align_vertical == NotificationVAlignment.bottom:
            y = self.parent().height() - self.height() - self._settings.space_vertical
        elif align_vertical == NotificationVAlignment.center:
            y = (self.parent().height() - self.height()) / 2
        else:
            raise ValueError(f"Alignment value {align_vertical} is not supported")

        self.move(
            self.parent().mapToGlobal(QPoint(x, y))  # type:ignore
        )
