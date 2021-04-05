#!/usr/bin/bash
python -m scripts.ingestion
python -m scripts.training
python -m scripts.scoring
python -m scripts.deployment
python -m scripts.reporting
python -m scripts.app
