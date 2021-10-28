import json
import os
import pytest
import koji
import requests
import yaml
import channel_validator as cv


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(TESTS_DIR, "fixtures")


class FakeCall:
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        call_dirs = ["getBuildLogs", "getBuild"]
        if self.name in call_dirs:
            filename = str(args[0]) + ".json"
            fixture = os.path.join(FIXTURES_DIR, "calls", self.name, filename)
        else:
            filename = self.name + ".json"
            fixture = os.path.join(FIXTURES_DIR, "calls", filename)
        try:
            with open(fixture) as fp:
                return json.load(fp)
        except FileNotFoundError:
            print("Create new fixture file at %s" % fixture)
            print("koji call %s ... --json-output > %s" % (self.name, fixture))
            raise


