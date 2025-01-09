# Copyright 2025 Wesley Piard
# SPDX-License-Identifier: GPL-3.0-or-later

import re

from aqt import mw, gui_hooks
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from aqt.webview import AnkiWebView, WebContent


def filter_kanji(input_string: str) -> str:
    """
    Filters a string to retain only Kanji characters.
    """
    kanji_pattern = r"[\u4E00-\u9FFF]"
    return "".join(re.findall(kanji_pattern, input_string))


def webview_schedule_kanji(wv: AnkiWebView):
    selected_kanji_str = filter_kanji(wv.selectedText())
    selected_kanji_list = list(selected_kanji_str)
    # showInfo("Kanji contained inside selected text: " + "".join(selected_kanji_list))

    if not selected_kanji_list:
        showInfo("No kanji in selection.")
        return
    else:
        # filter out any kanji in relevant decks that are already being learned
        # we only care about kanji that are still "new", so that we can schedule them
        new_kanji = []
        all_kanji = []
        new_cids = []
        all_cids = []
        for k in selected_kanji_list:
            tmp_cids = list(mw.col.find_cards(f"kanji:{k} -card:PRODUCTION is:new"))
            if tmp_cids:
                new_kanji.append(k)
                new_cids.extend(tmp_cids)

            tmp_cids = list(mw.col.find_cards(f"kanji:{k} -card:PRODUCTION"))
            if tmp_cids:
                all_kanji.append(k)
                all_cids.extend(tmp_cids)

        assert len(all_kanji) >= len(new_kanji)

        if not all_kanji:
            showInfo("The selected kanji do not exist in the deck.")

        if not new_kanji:
            showInfo("No new kanji in selection.")
            return
        else:
            # TODO: ask user for string of number/range of days to schedule
            # showInfo("New kanji to schedule: " + "".join(new_kanji))
            # showInfo(f"type of new_cids: {type(new_cids)}")
            # showInfo("New cids to schedule: " + ", ".join(str(c) for c in new_cids))
            mw.col.sched.set_due_date(new_cids, "0")
            showInfo("New kanji scheduled!\n" + "".join(new_kanji))
            return


def on_webview_context_menu(wv: AnkiWebView, m: QMenu) -> None:
    if mw.state == "review":
        a = m.addAction("Schedule Selected Kanji")
        a.triggered.connect(lambda: webview_schedule_kanji(wv))


# set gui hook such that "schedule kanji" option is added when user right clicks
gui_hooks.webview_will_show_context_menu.append(on_webview_context_menu)