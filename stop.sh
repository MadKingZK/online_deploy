#!/bin/bash

ps aux|grep gunicorn|grep -v grep|awk '{print $2}'|xargs kill


