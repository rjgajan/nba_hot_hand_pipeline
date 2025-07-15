SHELL   := /usr/bin/env bash
.ONESHELL:

CONFIG   := .player_config
RUN_BASE := runs

.PHONY: all findpid fetchppm montecarlo markov clean clean-config

all: clean-config findpid fetchppm montecarlo markov

clean-config:
	@rm -f $(CONFIG)

findpid:
	@set -e; \
	if [ ! -f $(CONFIG) ]; then \
	  read -rp "Enter player name (e.g. LeBron James): " PLAYER; \
	  read -rp "Enter seasons (space-separated in XXXX-XX format, e.g. 2016-17 2017-18): " -a SEASONS; \
	  SEASON_STR=$$(printf "%s-" "$${SEASONS[@]}"); \
	  SEASON_STR=$${SEASON_STR%-}; \
	  RUN_NAME=$$(printf "%s-%s" "$${PLAYER// /_}" "$$SEASON_STR"); \
	  RUN_DIR="$(RUN_BASE)/$$RUN_NAME"; \
	  printf 'PLAYER=\"%s\"\n' "$$PLAYER"      > $(CONFIG); \
	  printf 'SEASONS=(%s)\n' "$${SEASONS[*]}" >> $(CONFIG); \
	  printf 'RUN_DIR=\"%s\"\n' "$$RUN_DIR"    >> $(CONFIG); \
	fi; \
	source $(CONFIG); \
	mkdir -p "$$RUN_DIR"; \
	python3 -m src.find_player_id_cli "$$PLAYER" > "$$RUN_DIR/player_id.txt"

fetchppm: findpid
	@source $(CONFIG); \
	python3 -m src.get_ppm_cli \
	  --player-name "$$PLAYER" \
	  $$(cat "$$RUN_DIR/player_id.txt") \
	  "$$RUN_DIR/ppm_series.csv" \
	  "$$RUN_DIR/metadata.txt" \
	  $${SEASONS[@]}

montecarlo: fetchppm
	@source $(CONFIG); \
	python3 -m src.monte_carlo_cli \
		"$$RUN_DIR/ppm_series.csv" 1000 "$$RUN_DIR/monte_carlo.txt"

model: montecarlo
	@source $(CONFIG); \
	python3 -m src.arima_garch_cli \
		"$$RUN_DIR/ppm_series.csv" \
		"$$RUN_DIR/arima_garch.pkl" \
		--lags 20

markov: model
	@source $(CONFIG); \
	python3 -m src.markov_chain_cli \
		"$$RUN_DIR/ppm_series.csv" "$$RUN_DIR/markov_matrix.csv"

clean: clean-config
	@rm -rf "$(RUN_BASE)"