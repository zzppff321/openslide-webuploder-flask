#!/usr/bin/env python
# encoding: utf-8
# coding=utf-8
from com.uwsgidecorators import timer
from report.location import Location
from report.person import Person, Effect

@timer(600)
def ProcLocationReport(signum):
    Location.run()

@timer(1500)
def ProcPersonReport(signum):
    Person.run()

@timer(450)
def ProcPersonReport(signum):
    Effect.run()
