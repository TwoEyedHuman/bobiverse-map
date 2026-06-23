.PHONY: run web web-build web-preview

run:
	pipenv run streamlit run app.py

web:
	cd web && npm run dev

web-build:
	cd web && npm run build

web-preview:
	cd web && npm run preview
