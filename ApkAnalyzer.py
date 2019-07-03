#!/usr/bin/python3
#
# ApkAnalyzer.py: Takes an APK as an input and constructs features for analysis
#

from CodeParser import CodeParser
from bs4 import BeautifulSoup
from data import FeatureVector
from DexParser import DexParser
from message import *
from ngrams import *
import os
import settings
import subprocess


# Class for analyzing an APK file
class ApkAnalyzer:

    def __init__(self, apk_file):

        # Check if apk_file exists
        if not os.path.exists(apk_file):
            error('ApkAnalyzer', 'file not found: %s' % (apk_file))
            return

        self.file = apk_file            # APK file path
        self.dir = apk_file + '.dec'    # extracted APK directory

        # Check whether extraction directory exists
        self.dir_exists = os.path.exists(self.dir)
        if self.dir_exists:
            verb('ApkAnalyzer', 'found extraction directory %s' % (self.dir))

        self.ngrams = {}
        self.vector = FeatureVector()   # Feature vector
        self.dex = None                 # DexParser object
        self.code = []                  # Array of CodeParser objects


    # Extract/decrypt APK file using `apktool`
    def extract(self):

        # This is the command that extracts the APK file
        # Flags:
        #   d   This instructs apktool to decode an APK file
        #  -s   This prevents apktool from generating source code from classes.dex
        #  -o   This precedes the desired name of the output directory
        cmd = 'apktool d -s -o %s %s' % (self.dir, self.file)

        verb('extract', 'extracting %s to %s ...' % (self.file, self.dir))

        # Fork command
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        # Wait for command completion
        proc.wait()

        # If the process exited with errors, print its output
        if proc.returncode != 0:
            error('extract', 'encountered errors for %s' % (self.file))
            error('extract', '\n%s' % (proc.stderr.read().decode()) )
        else:
            verb('extract', 'extraction completed successfuly')

    # Load and parse DEX file
    def loadDex(self):

        self.dex = DexParser(os.path.join(self.dir, 'classes.dex'))

    # Get number of direct/virtual methods, static/instance fields, abstract methods
    def getClassFeatures(self):

        for cls in self.dex.class_defs:
            if cls.class_data is not None:
                self.vector.n_direct_methods += cls.class_data.direct_methods_size
                self.vector.n_virtual_methods += cls.class_data.virtual_methods_size
                self.vector.n_static_fields += cls.class_data.static_fields_size
                self.vector.n_instance_fields += cls.class_data.instance_fields_size

                # Direct methods
                for m in cls.class_data.direct_methods:
                    if m.code is None:
                        # Get number of abstract direct methods
                        self.vector.n_abstract_direct_methods += 1
                    elif m.code.tries_size != 0:
                        # Get number of methods with error handling
                        self.vector.n_error_handling_methods += 1
                        # Parse bytecode
                        self.code.append(CodeParser(m.code.insns,
                            self.dex.header.VERSION))

                # Virtual methods
                for m in cls.class_data.virtual_methods:
                    if m.code is None:
                        # Get number of abstract virtual methods
                        self.vector.n_abstract_virtual_methods += 1
                    elif m.code.tries_size != 0:
                        # Get number of methods with error handling
                        self.vector.n_error_handling_methods += 1
                        # Parse bytecode
                        self.code.append(CodeParser(m.code.insns,
                            self.dex.header.VERSION))

                # Static fields
                for f in cls.class_data.static_fields:
                    if f.access_flags.final:
                        # Get number of final static fields
                        self.vector.n_final_static_fields += 1

                # Instance fields
                for f in cls.class_data.instance_fields:
                    if f.access_flags.final:
                        # Get number of final instance fields
                        self.vector.n_final_instance_fields += 1

    def getCodeFeatures(self):

        for c in self.code:

            debug('getCodeFeatures', c)


    def getNgramFeatures(self, path="res/values/strings.xml"):

        path = os.path.join(self.dir, path)

        if not os.path.exists(path):
            error('get_n_grams', 'Path does not exist')

        with open(path) as xml_file:
            parser = BeautifulSoup(xml_file, features="lxml-xml")

        strings = parser.findAll("string")

        for i in range(len(strings)):
            strings[i] = bytes(strings[i].text, encoding='utf-8')

        self.ngrams = get_n_grams(strings)

        verb('getNgramFeatures', 'Successfully created ngrams')


    # Run entire analysis routine
    def run(self):

        if not self.dir_exists: self.extract()
        self.loadDex()
        self.getNgramFeatures()
        self.getClassFeatures()
        self.getCodeFeatures()


if __name__ == '__main__':

    import sys

    # TODO parse verbosity through argv

    settings.VERBOSE = True
    settings.NAME = sys.argv[0]

    if len(sys.argv) < 2:
        error(settings.NAME, '%s <apkFileName>' % (sys.argv[0]), True, pre='usage')

    analyzer = ApkAnalyzer(sys.argv[1])
    analyzer.run()
    # analyzer.loadDex()
    # analyzer.getClassFeatures()
    verb(settings.NAME, analyzer.vector)

