from django import template

register = template.Library()

def pluralize(num, string):
    return '%s %s%s'%(num, string, '' if num == 1 else 's')

@register.filter
def natural_timedelta(timedelta):
    """
    Transforms the timedelta to a human-readable representation.

    Note: Only works with positive timedeltas.
    """
    seconds = timedelta.total_seconds()
    assert seconds >= 0

    if seconds < 10:
        return '%.2f seconds' % seconds

    seconds = round(seconds, 1)

    if seconds < 60:
        return '%.1f seconds' % seconds

    labels = ['day', 'hour', 'minute', 'second']
    counts = [24*60*60, 60*60, 60, 1]
    for i, (count, label) in enumerate(zip(counts, labels)):
        if seconds >= count:
            num = int(seconds//count)
            output = pluralize(num, label)

            if num < 10 and i < len(labels):
                num_next = int((seconds - num * count) // counts[i + 1])
                if num_next > 0:
                    output += ', ' + pluralize(num_next, labels[i + 1])

            return output
