.PHONY: prettier-fix prettier-check

prettier-fix:
	npx prettier --write .

prettier-check:
	npx prettier --check .
