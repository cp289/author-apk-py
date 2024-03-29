#!/usr/bin/python3
#
# analysis.py: feature extraction from apk files
#

from CodeParser import CodeParser
from bs4 import BeautifulSoup
import data
from DexParser import DexParser
import math
from message import *
from multiprocessing import Pool
from ngrams import *
import os
import settings
import shutil
import subprocess

IMMEDIATE_LITERAL_TYPES = ("Const4", "Const16", "Const", "ConstHigh16",
        "ConstWide16", "ConstWide32", "ConstWide", "ConstWideHigh16")

UNARY_OPERATOR_TYPES = ("NegInt", "NotInt", "NegLong", "NotLong", "NegFloat",
    "NegDouble", "IntToLong", "IntToFloat", "IntToDouble", "LongToInt",
    "LongToFloat", "LongToDouble", "FloatToInt", "FloatToLong", "FloatToDouble",
    "DoubleToInt", "DoubleToLong", "DoubleToFloat", "IntToByte", "IntToChar",
    "IntToShort")

BINARY_OPERATOR_TYPES = ( "AddInt", "SubInt", "MulInt", "DivInt", "RemInt",
    "AndInt", "OrInt", "XorInt", "ShlInt", "ShrInt", "UshrInt", "AddLong",
    "SubLong", "MulLong", "DivLong", "RemLong", "AndLong", "OrLong", "XorLong",
    "ShlLong", "ShrLong", "UshrLong", "AddFloat", "SubFloat", "MulFloat",
    "DivFloat", "RemFloat", "AddDouble", "SubDouble", "MulDouble", "DivDouble",
    "RemDouble", "AddInt2Addr", "SubInt2Addr", "MulInt2Addr", "DivInt2Addr",
    "RemInt2Addr", "AndInt2Addr", "OrInt2Addr", "XorInt2Addr", "ShlInt2Addr",
    "ShrInt2Addr", "UshrInt2Addr", "AddLong2Addr", "SubLong2Addr",
    "MulLong2Addr", "DivLong2Addr", "RemLong2Addr", "AndLong2Addr",
    "OrLong2Addr", "XorLong2Addr", "ShlLong2Addr", "ShrLong2Addr",
    "UshrLong2Addr", "AddFloat2Addr", "SubFloat2Addr", "MulFloat2Addr",
    "DivFloat2Addr", "RemFloat2Addr", "AddDouble2Addr", "SubDouble2Addr",
    "MulDouble2Addr", "DivDouble2Addr", "RemDouble2Addr", "AddIntLit16",
    "SubIntLit16", "MulIntLit16", "DivIntLit16", "RemIntLit16", "AndIntLit16",
    "OrIntLit16", "XorIntLit16", "AddIntLit8", "SubIntLit8", "MulIntLit8",
    "DivIntLit8", "RemIntLit8", "AndIntLit8", "OrIntLit8", "XorIntLit8",
    "ShlIntLit8", "ShrIntLit8", "UshrIntLit8")

# Class for analyzing an APK file (does not perform TF-IDF analysis)
class ApkAnalyzer:

    def __init__(self, apk_file):

        self.finished = False

        # Check if apk_file exists
        if not os.path.exists(apk_file):
            error('ApkAnalyzer', 'file not found: %s' % (apk_file))
            return

        self.file = apk_file            # APK file path
        self.dir = apk_file + '.dec'    # extracted APK directory

        self.ngrams = {}                # Contains all the ngrams found in the apk
        self.vector = data.FeatureVector()  # Feature vector
        self.dex = None                 # DexParser object
        self.bytecode = []              # Array of bytecode sections
        self.code = []                  # Array of CodeParser objects


    # Extract/decrypt APK file using `apktool`
    def extract(self):

        # This is the command that extracts the APK file
        # Flags:
        #   d   This instructs apktool to decode an APK file
        #  -f   This deletes the destination directory if it exists
        #  -s   This prevents apktool from generating source code from classes.dex
        #  -o   This precedes the desired name of the output directory
        cmd = 'apktool d -f -s -o %s %s' % (self.dir, self.file)

        verb('extract', 'extracting %s to %s ...' % (self.file, self.dir))

        # Fork command
        with subprocess.Popen(cmd.split(), stdout=subprocess.PIPE,
                stderr=subprocess.PIPE) as proc:

            # Wait for command completion
            proc.wait()

            # If the process exited with errors, print its output
            if proc.returncode != 0:
                error('extract', 'encountered errors for %s' % (self.file))
                error('extract', '\n%s' % (proc.stderr.read().decode()) )
            else:
                verb('extract', 'extraction completed successfuly')
    
    # Remove extracted directory
    def remove(self):
        verb('remove', 'delete extracted directory %s' % (self.dir))
        shutil.rmtree(self.dir, ignore_errors=True)

    # Load and parse DEX file
    def loadDex(self):

        self.dex = DexParser(os.path.join(self.dir, 'classes.dex'))

    # Get number of direct/virtual methods, static/instance fields, abstract methods
    def getClassFeatures(self):

        verb('getClassFeatures', 'Extracting class features...')
        for cls in self.dex.class_defs:
            if cls.class_data is not None:
                self.vector.n_direct_methods += cls.class_data.direct_methods_size
                self.vector.n_virtual_methods += cls.class_data.virtual_methods_size
                self.vector.n_total_static_fields += cls.class_data.static_fields_size
                self.vector.n_total_instance_fields += cls.class_data.instance_fields_size

                # Direct methods
                for m in cls.class_data.direct_methods:
                    if m.code is None:
                        # Get number of abstract direct methods
                        self.vector.n_abstract_direct_methods += 1
                    elif m.code.tries_size != 0:
                        # Get number of methods with error handling
                        self.vector.n_error_handling_methods += 1
                        # Store bytecode
                        self.bytecode.append(m.code.insns)
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
                        # Store bytecode
                        self.bytecode.append(m.code.insns)
                        # Parse bytecode
                        self.code.append(CodeParser(m.code.insns,
                            self.dex.header.VERSION))

                # Static fields
                for f in cls.class_data.static_fields:
                    if f.access_flags.final:
                        # Get number of final static fields
                        self.vector.n_total_final_static_fields += 1

                # Instance fields
                for f in cls.class_data.instance_fields:
                    if f.access_flags.final:
                        # Get number of final instance fields
                        self.vector.n_total_final_instance_fields += 1

    # Get features from bytecode
    def getCodeFeatures(self):

        for c in self.code:
            for ins in c.insns:
                if ins.name in IMMEDIATE_LITERAL_TYPES:
                    self.vector.n_total_immediate_constants += 1
                if ins.name in UNARY_OPERATOR_TYPES:
                    self.vector.n_total_unary_operators += 1
                if ins.name in BINARY_OPERATOR_TYPES:
                    self.vector.n_total_binary_operators += 1

    def getNgramFeatures(self, path="res/values/strings.xml"):

        path = os.path.join(self.dir, path)

        if not os.path.exists(path):
            error('get_n_grams', 'Path %s does not exist' % (path))
            return

        with open(path) as xml_file:
            parser = BeautifulSoup(xml_file, features="lxml-xml")

        strings = parser.findAll("string")

        for i in range(len(strings)):
            strings[i] = bytes(strings[i].text, encoding='utf-8')

        # Begin by parsing ngrams from `path`
        self.ngrams = get_n_grams(strings)

        # Next parse ngrams from code sections
        data.updateOccurrences(self.ngrams, get_n_grams(self.bytecode))

        verb('getNgramFeatures', 'Successfully extracted %d ngrams' %
                (len(self.ngrams)))

    # Add top_n ngrams to the feature vector sorted by TF-IDFs in self.ngrams
    def getTfidfFeatures(self, top_n=5):
        # Sort ngrams by TF-IDF
        ngrams_sorted = sorted(self.ngrams, key=self.ngrams.get, reverse=True)
        verb('getTfidfFeatures', ngrams_sorted[:top_n])

        # Store top 5 ngrams each as a number
        self.vector.top_ngrams = (int.from_bytes(ngrams_sorted[i], 'little') for
                i in range(top_n))

    # Debug
    def _debug(self):
        for cls in self.dex.class_defs:
            if cls.class_data is not None:
                # Direct methods
                for m in cls.class_data.direct_methods[0:1]:
                    if m.code is not None:
                        verb('debug', 'code:%s' % (hex(m.code_off)))

                # Virtual methods
                for m in cls.class_data.virtual_methods[0:1]:
                    if m.code is not None:
                        verb('debug', 'code:%s' % (hex(m.code_off)))
        verb('debug', self.dex.map)

    # Remove references to bulky objects to allow garbage collection
    def clean(self):
        del self.dex
        del self.bytecode
        del self.code

    # Run entire analysis routine
    def run(self):

        try:
            self.extract()
            self.loadDex()
            self.getClassFeatures()
            self.getNgramFeatures()
            self.getCodeFeatures()
            self.clean()
            self.finished = True
        finally:
            self.remove()
        return self


# Object for parsing/labeling a set of Apks (performs TF-IDF analysis)
class ApkSet:

    def __init__(self, directory, exclude=set()):

        self.directory = directory
        self.apks = []
        self.n_apks = 0
        self.exclude = exclude
    
    # Enumerate all APK files
    def enumApks(self):

        for base, dirs, files in os.walk(self.directory):
            # Restrict to .apk extension
            files = [f for f in files if os.path.splitext(f)[1] == '.apk' and
                    os.path.join(base, f) not in self.exclude]
            for f in files:
                self.apks.append(ApkAnalyzer(os.path.join(base,f)))

        self.n_apks = len(self.apks)


    # Calculate Tf-Idf features
    def getTfidfFeatures(self):

        ngram_docs = {}

        # Calculate parts of TF-IDF values (overwrites occurrences in apk.ngrams)
        for apk in self.apks:
            total = sum(apk.ngrams.values())
            for ngram in apk.ngrams:
                # Compute TF term for ngram
                apk.ngrams[ngram] /= total
                # Compute number of documents with ngram in it
                if ngram in ngram_docs:
                    ngram_docs[ngram] += 1
                else:
                    ngram_docs[ngram] = 1

        # Calculate IDFs (overwrites TFs in apk.ngrams)
        log_total_docs = math.log(self.n_apks)
        for apk in self.apks:
            for ngram in apk.ngrams:
                apk.ngrams[ngram] *= log_total_docs - math.log(ngram_docs[ngram])
            apk.getTfidfFeatures()

    # Can't use a lambda since it breaks multiprocessing
    def _run(self, apk):
        return apk.run()

    # Run author-apk
    def run(self):

        self.enumApks()

        if settings.PARALLEL:
            new_apks = []
            try:
                with Pool(settings.N_THREADS) as pool:
                    itr = pool.imap_unordered(self._run, self.apks)
                    for i in itr:
                        new_apks.append(i)
            finally:
                self.apks = new_apks
        else:
            for apk in self.apks:
                apk.run()

        if self.n_apks > 0:
            self.getTfidfFeatures()


if __name__ == '__main__':

    import sys

    # TODO parse verbosity through argv

    settings.VERBOSE = True
    settings.DEBUG = True
    settings.DEBUG_FILTER = ('CodeParser',)

    if len(sys.argv) < 2:
        error(settings.NAME, '%s <apkDirectories...>' % (settings.NAME), True, pre='usage')

    aset = ApkSet(*sys.argv[1:])
    aset.run()
    verb(settings.NAME, '\n'.join([format(i.vector) for i in main.apks]))

