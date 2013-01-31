"""Middleware for profiling a http request."""

import cProfile
import cStringIO
import logging
import pstats

from django.conf import settings
from django.core import exceptions
from django.db import connection


class ProfilerMiddleware(object):
  """Middleware for profiling a http request.

  This middleware will only be active when settings.DEBUG is True, and
  settings.PROFILER exists. The output of the profiler will be printed into
  a logger specified in settings.PROFILER (default to logging.info)

  The settings.PROFILER is a dictionary that can have the following key words:
    display_profiler: Show profiler info for each response, default to True
    sort_by: Sorting order of profiler, default to ('time', 'calls'), see
        http://docs.python.org/2/library/profile.html#pstats.Stats.sort_stats
        for more options.
    restrictions: Lines of profile to print, default to 20 for 20 lines, see
        http://docs.python.org/2/library/profile.html#pstats.Stats.print_stats
        for detail.
    display_sql: Takes value from 0 to 3, default to 0
        0: Not displaying sql queries
        1: Only display summary of number of sql queries and times taken.
        2: Only display top n most time consuming sql queries, n is set by
           top_n_sql.
        3: Display all sql queries
    top_n_sql: Only effective if display_sql is 2. Display top n most time
        consuming sql queries.
    logger: Output target for profiler, sql queryies informations. This must be
        a callable. Default to logging.info.
  """

  def __init__(self):
    if not settings.DEBUG or not hasattr(settings, 'PROFILER'):
      raise exceptions.MiddlewareNotUsed()

    self._display_profiler = settings.PROFILER.get('display_profiler', True)
    self._sort_by = settings.PROFILER.get('sort_by', ('time', 'calls'))
    self._restrictions = settings.PROFILER.get('restrictions', 20)

    self._logger = settings.PROFILER.get('logger', logging.info)

    self._display_sql = settings.PROFILER.get('display_sql', 0)
    self._top_n_sql = settings.PROFILER.get('top_n_sql', 10)

  def process_view(self, request, callback, callback_args, callback_kwargs):
    if settings.DEBUG and self._display_profiler:
      self.profiler = cProfile.Profile()
      args = (request,) + callback_args
      return self.profiler.runcall(callback, *args, **callback_kwargs)

  def process_response(self, request, response):
    """Output profiler info after response."""
    if settings.DEBUG and self._display_profiler:
      self.profiler.create_stats()
      profiler_out = cStringIO.StringIO()
      profiler_out.write('------ profiler for %s -----\n' % request.path)
      stats = pstats.Stats(self.profiler, stream=profiler_out)
      stats.sort_stats(*self._sort_by).print_stats(self._restrictions)
      self._logger(profiler_out.getvalue())

    if settings.DEBUG and self._display_sql:
      sql_out = cStringIO.StringIO()
      query_cnt = len(connection.queries)
      query_time = sum(float(query['time']) for query in connection.queries)
      sql_out.write(('-------- sql queries for %s: %s quries, '
                     'roughly %.4f seconds-------\n') %
                    (request.path, query_cnt, query_time))

      if self._top_n_sql and self._display_sql == 2:
        top_n_sqls = sorted(connection.queries, key=lambda x: -float(x['time']))
        sql_out.write('\n'.join('(%s) %s' % (q['time'], q['sql'])
                                for q in top_n_sqls[:self._top_n_sql]))

      if self._display_sql == 3:
        sql_out.write('\n'.join('(%s) %s' % (q['time'], q['sql'])
                                for q in connection.queries))
      self._logger(sql_out.getvalue())

    return response
