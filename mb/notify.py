"""The weekly reminder that the record has drifted from the machine."""
import subprocess

SHOWN = 5


def message(diffs):
    """(title, body) for the notification, or None when state/ is current."""
    if not diffs:
        return None
    more = f"\n... and {len(diffs) - SHOWN} more" if len(diffs) > SHOWN else ""
    body = "\n".join(diffs[:SHOWN]) + more + "\nRun: python3 -m mb capture, review, commit."
    return f"{len(diffs)} change(s) not in the machine record", body


def send(title, body):
    subprocess.run(["notify-send", "--app-name=machine-bootstrap", "--icon=dialog-information", title, body])


def timer_units(project_dir):
    service = (
        "[Unit]\nDescription=Check that the machine record (machine-bootstrap) is current\n\n"
        f"[Service]\nType=oneshot\nWorkingDirectory={project_dir}\n"
        "ExecStart=/usr/bin/python3 -m mb status --notify\nSuccessExitStatus=0 1\n"
    )
    timer = (
        "[Unit]\nDescription=Weekly check of the machine record\n\n"
        "[Timer]\nOnCalendar=weekly\nPersistent=true\nRandomizedDelaySec=1h\n\n"
        "[Install]\nWantedBy=timers.target\n"
    )
    return service, timer
