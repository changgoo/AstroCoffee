SITE_DIR := _site

.PHONY: build serve clean

build:
	python ./src/create_calendars.py
	mkdir -p $(SITE_DIR)/data
	cp calendar/index.html $(SITE_DIR)/
	cp calendar/calendar.js $(SITE_DIR)/
	cp calendar/style.css $(SITE_DIR)/
	cp calendar/periods.json $(SITE_DIR)/
	cp data/hosts_*.json $(SITE_DIR)/data/
	cp data/holidays_*.json $(SITE_DIR)/data/

serve: build
	python -m http.server 8080 --directory $(SITE_DIR)

clean:
	rm -rf $(SITE_DIR)
