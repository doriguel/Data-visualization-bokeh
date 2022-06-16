"""Lists of column names from the input database."""

categories = ['name', 'origin', 'mfr']

floats_metric = ['mpg',
            'displ',
            'accel']

ints_metric = ['cyl',
            'hp',
            'weight_kg',
            'yr']

floats_imper = ['mpg',
            'displ',
            'accel']

ints_imper = ['cyl',
            'hp',
            'weight_lbs',
            'yr']

xy_options = sorted(floats_metric + ints_metric)
xy_options_imper = sorted(floats_imper + ints_imper)

colorby_options = sorted(categories[1:])

resizeby_options = sorted(floats_metric + ints_metric)
resizeby_options_imper = sorted(floats_imper + ints_imper)
