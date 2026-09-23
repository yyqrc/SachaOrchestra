"""Small source model. Production snapshots contain more pixels and geometry."""
from copy import deepcopy


def load_snapshot():
    return {
        'width': 8, 'height': 1,
        'rgb': [0, 0, 1, 0, 0, 3, 0, 0],
        'shadow': [0, 0, .2, 0, 0, .8, 0, 0],
        'support': [False, False, True, False, False, True, False, False],
        'uv_inside': [False, False, True, False, False, True, False, False],
        'pairs': [{'global_id': 37, 'object_id': 2, 'a': 2, 'b': 5},
                  {'global_id': 20, 'object_id': 3, 'a': 1, 'b': 6}],
    }


def targets(snapshot, radius):
    sources = [i for i, value in enumerate(snapshot['support']) if value]
    return [not value and any(abs(i - source) <= radius for source in sources)
            for i, value in enumerate(snapshot['support'])]


def run(snapshot, channel, radius=1, stage='stitch'):
    if channel not in ('rgb', 'shadow'):
        raise ValueError('unknown channel')
    if stage not in ('input', 'coverage', 'fill', 'stitch'):
        raise ValueError('unknown stage')
    result = deepcopy(snapshot)
    result['pixels'] = snapshot[channel][:]
    result['target'] = targets(snapshot, radius)
    if stage in ('fill', 'stitch'):
        sources = [i for i, value in enumerate(snapshot['support']) if value]
        for i, value in enumerate(result['target']):
            if value:
                source = min(sources, key=lambda s: (abs(i - s), s))
                result['pixels'][i] = snapshot[channel][source]
    if stage == 'stitch':
        result['pixels'][2] = result['pixels'][5] = (snapshot[channel][2] + snapshot[channel][5]) / 2
    result['stage'] = stage
    return result


def read_raw_image():
    return {'pixels': [0, 0, 1, 0, 0, 3, 0, 0]}


def run_self_test():
    return run(load_snapshot(), 'rgb')['pixels'][2] == 2
