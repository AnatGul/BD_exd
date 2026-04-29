Yes — Entrypoint is run.py; avoid invoking main.py or translator.py directly to prevent import issues.

Yes — Data flows: inputs in data/input, outputs in data/output; run.py operates on data/input by default.

Yes — Use a virtual environment and install dependencies from requirements.txt to ensure reproducible runs.

Yes — Some fields are not translated (see README under "Не переводятся"); follow those exceptions.

Yes — Address transformations exist for Russia (e.g., Rostov-on-Don) and Bangladesh; apply exactly as documented.

Yes — Company name transformations exist (e.g., Gloria Jeans) and should be applied per the rules.

Yes — Field translation/mapping for the 51 fields is defined in the README; rely on that as canonical guidance.

Yes — To test, place sample inputs in data/input and run: python run.py; verify outputs in data/output.

Yes — Ensure Python 3.12+ is used; mismatched versions can cause syntax/import errors.

Yes — If an ImportError occurs when running modules directly, switch to running via run.py.

Yes — Consult README.md first for high-signal repo conventions and usage; do not assume defaults.
