
Django middleware for profiling a http request.

This middleware will only be active when settings.DEBUG is True, and settings.PROFILER exists. The output of the profiler will be printed into a logger specified in settings.PROFILER (default to logging.info)

The settings.PROFILER is a dictionary that can have the following key words:
   * display_profiler: Show profiler info for each response, default to True
   * sort_by: Sorting order of profiler, default to ('time', 'calls'), see http://docs.python.org/2/library/profile.html#pstats.Stats.sort_stats for more options.
   * restrictions: Lines of profile to print, default to 20 for 20 lines, see http://docs.python.org/2/library/profile.html#pstats.Stats.print_stats for detail.
   * display_sql: Takes value from 0 to 3, default to 0
       ** 0: Not displaying sql queries
       ** 1: Only display summary of number of sql queries and times taken.
       ** 2: Only display top n most time consuming sql queries, n is set by top_n_sql.
       ** 3: Display all sql queries
    * top_n_sql: Only effective if display_sql is 2. Display top n most time consuming sql queries.
    * logger: Output target for profiler, sql queryies informations. This must be a callable. Default to logging.info

Adopted from:
   * https://gist.github.com/1229681
   * https://gist.github.com/1229685
