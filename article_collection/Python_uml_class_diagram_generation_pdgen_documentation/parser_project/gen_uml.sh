#!/bin/bash
pyreverse --only-classnames --colorized -o png -p le_audio_utilities \
    main.py le_report_data.py le_audio_parsing_data.py le_patterns.py \
    le_audio_log_event_publisher.py general_data.py errors.py \
    constants.py observer/*.py le_audio_constants.py le_report_gen_utils.py
