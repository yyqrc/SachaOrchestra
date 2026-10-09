"""Small executable editor-material flow, not Unity production code."""

from dataclasses import dataclass, field


@dataclass
class State:
    materials: dict
    renderers: dict
    prefabs: dict = field(default_factory=dict)
    events: list = field(default_factory=list)
    errors: list = field(default_factory=list)


def collect_renderers(batch):
    return batch['ordinary'] + batch['outdoor']


def resolve_raw(material, batch):
    if material in batch['raw_assets']:
        return material, None
    matches = {row['raw'] for row in batch['relations']
               if material in row['tod'] and row['raw'] in batch['raw_assets']}
    if len(matches) == 1:
        return next(iter(matches)), None
    return None, 'conflicting mapping' if len(matches) > 1 else 'missing raw material'


def create_tod_material(raw, batch, state):
    name = batch['group'] + '_' + raw + '_TOD'
    state.materials[name] = {'raw': raw, 'lightmap': batch['lightmap']}
    state.events.append(('material', name))
    return name


def apply_renderer(renderer, materials, batch, state):
    state.renderers[renderer['id']] = {
        'materials': list(materials), 'lightmap': batch['lightmap']}
    state.events.append(('apply', renderer['id']))


def save_prefabs(renderers, state):
    for renderer in renderers:
        state.prefabs[renderer['id']] = dict(state.renderers[renderer['id']])
    state.events.append(('save', tuple(renderer['id'] for renderer in renderers)))


def cleanup_materials(state):
    used = {material for renderer in state.renderers.values()
            for material in renderer['materials']}
    for name in list(state.materials):
        if name.endswith('_TOD') and name not in used:
            del state.materials[name]
    state.events.append(('cleanup',))


def bake(batch, state):
    state.events.append(('bake', batch['lightmap']))


def process_batch(batch, state):
    bake(batch, state)
    renderers = collect_renderers(batch)
    for renderer in renderers:
        materials = []
        for material in renderer['materials']:
            raw, error = resolve_raw(material, batch)
            if error:
                break
            materials.append(create_tod_material(raw, batch, state))
        else:
            apply_renderer(renderer, materials, batch, state)
    save_prefabs(renderers, state)
    cleanup_materials(state)
