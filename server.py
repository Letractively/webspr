# Copyright (c) 2007, Alex Drummond <a.d.drummond@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY Alex Drummond ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Alex Drummond BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from paste import httpserver
import json
import itertools
import StringIO
import md5
import time as time_module
import types

PORT = 3000
RESULT_FILE_NAME = "results"
RAW_RESULT_FILE_NAME = "raw_results"

class HighLevelParseError(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)

class Row(object):
    __slots__ = ['words', 'times', 'newlines', 'type', 'sentence', 'ip_hash', 'answer']
    def __init__(self, **args):
        for k, v in args.iteritems():
            setattr(self, k, v)

class ResultSet(object):
    def __init__(self, rows):
        self.rows = rows

    def __repr__(self):
        return "ResultSet(%s)" % str(self.rows)

    def to_csv(self):
        thetime = time_module.time()
        out = StringIO.StringIO()
        for row in self.rows:
            sentence = ' '.join(row.words)
            sentence_md5 = md5.md5(sentence).hexdigest()
            for j, time, word, nl in itertools.izip(itertools.count(1), row.times, row.words, row.newlines):
                out.write(
                    "%i,%i,%i,%i,%i,%i,%i,%i,%s,%s\n" % \
                    (thetime, row.sentence, j, row.type, time, nl, row.answer, len(word), row.ip_hash, sentence_md5)
                )
        return out.getvalue()

def rearrange(parsed_json, ip):
    if len(parsed_json) != 4:
        raise HighLevelParseError()
    sentences = parsed_json[0]
    times = parsed_json[1]
    answers = parsed_json[2]
    newlines = parsed_json[3]
    if len(sentences) != len(times):
        raise HighLevelParseError()

    rows = []
    for s, t, a, nl in itertools.izip(sentences, times, answers, newlines):
        if (not (type(s) == types.DictType and s.has_key('words') and s.has_key('type') and s.has_key('num'))) or \
           len(s['words']) - 1 != len(t) or (not (a == 0 or a == 1 or a == -1)):
            raise HighLevelParseError()
        rows.append(Row(words=s['words'], times=t, newlines=nl, type=s['type'], sentence=s['num'], ip_hash=md5.md5(ip).hexdigest(), answer=a))
    return ResultSet(rows)

def control(env, start_response):
    ip = None
    if env.has_key('HTTP_X_FORWARDED_FOR'):
        ip = env['HTTP_X_FORWARDED_FOR']
    else:
        ip = env['REMOTE_ADDR']

    uri = env['PATH_INFO'] + ((env.has_key('QUERY_STRING') and env['QUERY_STRING']) and '?' + env['QUERY_STRING'] or '')
    stripped_uri = uri.strip('/');
    if stripped_uri == 'spr.html' or stripped_uri.endswith('data.js'): 
        contents = None
	f = None
        try:
            f = open(stripped_uri)
            contents = f.read()
        except IOError:
            start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
            return ["<html><body><h1>500 Internal Server Error</h1></body></html>"]
        finally:
            if f: f.close()
        start_response('200 OK', [('Content-Type', (stripped_uri == 'spr.html' and 'text/html' or 'text/javascript') +'; charset=utf-8')])
        return [contents]
    elif uri.strip('/') == 'send-results':
        if not (env['REQUEST_METHOD'] == 'POST') and (env.has_key('CONTENT_LENGTH')):
            start_response('400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')])
            return ["<html><body><h1>400 Bad Request</h1></body></html>"]

        content_length = None
        try:
            content_length = int(env['CONTENT_LENGTH'])
        except ValueError:
            start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
            return ["<html><body><h1>500 Internal Server Error</h1></body></html>"]

        post_data = env['wsgi.input'].read(content_length)

        # Keep a backup of the raw post data.
        bf = None
        try:
            bf = open(RAW_RESULT_FILE_NAME, "a")
            bf.write(post_data)
        except:
            pass
        finally:
            if bf: bf.close()

	rf = None
        try:
            parsed_json = json.read(post_data)
            rf = open(RESULT_FILE_NAME, "a")
            rf.write(rearrange(parsed_json, ip).to_csv())
            start_response('200 OK', [('Content-Type', 'text/plain; charset=ascii')])
            return ["OK"]
        except (json.ReadException, HighLevelParseError), e:
            start_response('400 Bad Request', [('Content-Type', 'text/html; charset=utf-8')])
            return ["<html><body><h1>400 Bad Request</h1></body></html>"]
        except IOError:
            start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
            return ["<html><body><h1>500 Internal Server Error</h1></body></html>"]
        finally:
            if rf: rf.close()
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html; charset=utf-8')])
        return ["<html><body><h1>404 Not Found</h1></body></html>"]

httpserver.serve(control, port=PORT)

