"""Business checks; no rule keywords, source-shape or line-count assertions."""

import copy
import unittest
from unittest.mock import patch

import postprocess as p


def inputs():
    wall = {'id': 'wall', 'name': 'Wall', 'materials': ['old_brick_TOD']}
    outdoor = {'id': 'yard', 'name': 'Yard', 'materials': ['lost_TOD', 'brick']}
    batch = {'group': 'Day', 'lightmap': 'lm_new', 'ordinary': [wall],
             'outdoor': [wall, outdoor], 'raw_assets': {'brick', 'stone'},
             'relations': [{'raw': 'brick', 'tod': ['old_brick_TOD']}]}
    state = p.State(
        materials={name: {} for name in
                   ['old_brick_TOD', 'lost_TOD', 'unused_TOD', 'external_TOD']},
        renderers={'wall': {'materials': ['old_brick_TOD'], 'lightmap': 'lm_old'},
                   'yard': {'materials': ['lost_TOD', 'brick'], 'lightmap': 'lm_old'},
                   'external': {'materials': ['external_TOD'], 'lightmap': 'lm_old'}})
    return batch, state


class MaterialFlowTests(unittest.TestCase):
    def test_manual_check_has_no_side_effects(self):
        batch, state = inputs()
        before = copy.deepcopy((batch, state))
        errors = p.check_materials(batch, state)
        self.assertEqual((batch, state), before)
        self.assertEqual(len(errors), 1)
        detail = str(errors[0])
        self.assertIn('Yard', detail)
        self.assertIn('lost_TOD', detail)
        self.assertTrue('missing' in detail.lower() or '缺' in detail or '找不到' in detail)

    def test_local_error_still_applies_saves_and_cleans(self):
        batch, state = inputs()
        with patch.object(p, 'save_prefabs', wraps=p.save_prefabs) as save, \
                patch.object(p, 'cleanup_materials', wraps=p.cleanup_materials) as clean:
            p.process_batch(batch, state)
        self.assertEqual(save.call_count, 1)
        self.assertEqual(clean.call_count, 1)
        self.assertEqual(state.renderers['yard'],
                         {'materials': ['lost_TOD', 'Day_brick_TOD'], 'lightmap': 'lm_new'})
        self.assertEqual(state.prefabs['yard'], state.renderers['yard'])
        self.assertIn('lost_TOD', state.materials)
        self.assertIn('external_TOD', state.materials)
        self.assertNotIn('unused_TOD', state.materials)
        self.assertEqual(len(state.errors), 1)
        self.assertEqual([x for x in state.events if x[0] == 'apply'],
                         [('apply', 'wall'), ('apply', 'yard')])
        self.assertEqual([x[0] for x in state.events][-2:], ['save', 'cleanup'])

    def test_conflict_preserves_material_and_reports_reason(self):
        batch, state = inputs()
        batch['outdoor'] = []
        batch['relations'].append({'raw': 'stone', 'tod': ['old_brick_TOD']})
        p.process_batch(batch, state)
        self.assertEqual(state.renderers['wall'],
                         {'materials': ['old_brick_TOD'], 'lightmap': 'lm_new'})
        self.assertEqual(len(state.errors), 1)
        self.assertIn('Wall', str(state.errors[0]))
        self.assertTrue('conflict' in str(state.errors[0]).lower() or '冲突' in str(state.errors[0]))

    def test_prepare_once_before_bake_not_per_renderer(self):
        batch, state = inputs()
        batch['outdoor'] = []

        class ObservedRelations(list):
            scans = 0

            def __iter__(self):
                self.scans += 1
                return super().__iter__()

        relations = ObservedRelations(batch['relations'])
        batch['relations'] = relations
        original_bake = p.bake

        def observe_bake(current, target):
            self.assertGreater(relations.scans, 0, 'material resolution must precede bake')
            self.assertEqual(target.events, [], 'preparation must not write assets')
            self.assertEqual(target.errors, [], 'errors are reported after processing')
            original_bake(current, target)

        batch['ordinary'] *= 20
        with patch.object(p, 'bake', side_effect=observe_bake):
            p.process_batch(batch, state)
        self.assertEqual(relations.scans, 1, 'one relation scan per batch, not per slot')

    def test_duplicate_mapping_is_not_a_conflict(self):
        batch, state = inputs()
        batch['outdoor'] = []
        batch['relations'].append({'raw': 'brick', 'tod': ['old_brick_TOD']})
        p.process_batch(batch, state)
        self.assertEqual(state.errors, [])
        self.assertEqual(state.renderers['wall'],
                         {'materials': ['Day_brick_TOD'], 'lightmap': 'lm_new'})

    def test_invalid_raw_does_not_hide_a_conflict(self):
        batch, state = inputs()
        batch['outdoor'] = []
        batch['relations'].append({'raw': 'absent', 'tod': ['old_brick_TOD']})
        p.process_batch(batch, state)
        self.assertEqual(state.renderers['wall'],
                         {'materials': ['old_brick_TOD'], 'lightmap': 'lm_new'})
        self.assertEqual(len(state.errors), 1)
        detail = str(state.errors[0])
        self.assertIn('Wall', detail)
        self.assertIn('old_brick_TOD', detail)
        self.assertTrue('conflict' in detail.lower() or '冲突' in detail)

    def test_each_failed_slot_reports_and_later_slots_continue(self):
        batch, state = inputs()
        batch['ordinary'] = []
        yard = batch['outdoor'][1]
        yard['materials'] = ['lost_TOD', 'lost_TOD', 'brick']
        batch['outdoor'] = [yard, yard]
        p.process_batch(batch, state)
        self.assertEqual(state.renderers['yard'],
                         {'materials': ['lost_TOD', 'lost_TOD', 'Day_brick_TOD'],
                          'lightmap': 'lm_new'})
        self.assertEqual(len(state.errors), 2)
        for error in state.errors:
            detail = str(error)
            self.assertIn('Yard', detail)
            self.assertIn('lost_TOD', detail)
            self.assertTrue('missing' in detail.lower() or '缺' in detail or '找不到' in detail)
        self.assertEqual([x for x in state.events if x[0] == 'apply'],
                         [('apply', 'yard')])

    def test_raw_identity_is_exact_without_name_guessing(self):
        for material in ('Brick', 'brick_TOD', 'Day_brick_TOD'):
            with self.subTest(material=material):
                batch, state = inputs()
                batch['outdoor'] = []
                batch['ordinary'][0]['materials'] = [material]
                p.process_batch(batch, state)
                self.assertEqual(state.renderers['wall'],
                                 {'materials': [material], 'lightmap': 'lm_new'})
                self.assertEqual(len(state.errors), 1)
                detail = str(state.errors[0])
                self.assertIn(material, detail)
                self.assertTrue('missing' in detail.lower() or '缺' in detail or '找不到' in detail)

    def test_next_bake_does_not_reuse_manual_check_or_previous_batch(self):
        batch, state = inputs()
        p.check_materials(batch, state)
        batch['relations'].append({'raw': 'stone', 'tod': ['lost_TOD']})
        p.process_batch(batch, state)
        self.assertEqual(state.errors, [])
        self.assertEqual(state.renderers['yard']['materials'][0], 'Day_stone_TOD')
        batch['relations'][-1]['raw'] = 'brick'
        batch['lightmap'] = 'lm_next'
        p.process_batch(batch, state)
        self.assertEqual(state.renderers['yard']['materials'][0], 'Day_brick_TOD')
        self.assertEqual(state.renderers['yard']['lightmap'], 'lm_next')


if __name__ == '__main__':
    unittest.main(verbosity=2)
