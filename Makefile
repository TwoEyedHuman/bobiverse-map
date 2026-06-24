.PHONY: web web-build web-preview

web:
	cd web && npm run dev

web-build:
	cd web && npm run build

web-preview:
	cd web && npm run preview
