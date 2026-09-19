# -*- coding: utf-8 -*-
"""MWeaver 랜딩 페이지 공지 배너 편집기.
notice.html을 수정하고 git commit/push까지 자동 수행한다.
내용을 비우고 저장하면 배너가 숨겨진다.
"""
import os
import re
import subprocess
import threading
import tkinter as tk
import webbrowser

DIR = os.path.dirname(os.path.abspath(__file__))
NOTICE = os.path.join(DIR, "notice.html")


def load_notice():
    if not os.path.exists(NOTICE):
        return ""
    with open(NOTICE, "r", encoding="utf-8") as f:
        return re.sub(r"<br\s*/?>", "\n", f.read()).strip()


def run_git(*args):
    return subprocess.run(
        ["git", *args], cwd=DIR, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    )


def save():
    text = txt.get("1.0", "end-1c").strip()
    html = "<br>".join(text.splitlines())
    btn.config(state="disabled")
    status.config(text="저장 및 배포 중...")

    def done(msg):
        root.after(0, lambda: (status.config(text=msg), btn.config(state="normal")))

    def work():
        try:
            with open(NOTICE, "w", encoding="utf-8", newline="\n") as f:
                f.write(html + ("\n" if html else ""))
            run_git("add", "notice.html")
            c = run_git("commit", "-m", "Update notice banner")
            if c.returncode != 0:
                if "nothing to commit" in (c.stdout + c.stderr):
                    done("변경 사항 없음 (이미 동일한 내용)")
                else:
                    done("커밋 실패: " + (c.stderr or c.stdout).strip()[:200])
                return
            p = run_git("push", "origin", "master")
            if p.returncode == 0:
                done("저장 및 배포 완료 (1~2분 후 사이트 반영)")
            else:
                done("푸시 실패: " + (p.stderr or p.stdout).strip()[:200])
        except Exception as e:
            done("오류: " + str(e)[:200])

    threading.Thread(target=work, daemon=True).start()


root = tk.Tk()
root.title("공지 배너 편집")
root.geometry("560x230")

tk.Label(
    root,
    text='공지 내용 (비우고 저장하면 배너 숨김 / <a href="URL"> 등 HTML 태그 사용 가능):',
).pack(anchor="w", padx=10, pady=(10, 4))
txt = tk.Text(root, height=4, wrap="word", font=("Malgun Gothic", 10))
txt.pack(fill="both", expand=True, padx=10)
txt.insert("1.0", load_notice())

btn_frame = tk.Frame(root)
btn_frame.pack(pady=8)
btn = tk.Button(btn_frame, text="저장 및 배포", command=save)
btn.pack(side="left", padx=4)
tk.Button(
    btn_frame, text="랜딩 페이지 열기",
    command=lambda: webbrowser.open("https://25joshua.github.io/mweaver-landing/"),
).pack(side="left", padx=4)
status = tk.Label(root, text="", fg="gray")
status.pack(pady=(0, 8))

root.mainloop()
