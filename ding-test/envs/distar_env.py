from distar.envs.env import SC2Env

from ding.envs import BaseEnv
from distar.agent.default.lib.actions import ACTIONS, NUM_ACTIONS
from distar.agent.default.lib.features import MAX_DELAY, SPATIAL_SIZE, MAX_SELECTED_UNITS_NUM
from distar.pysc2.lib.action_dict import ACTIONS_STAT
import torch
import random

class DIStarEnv(SC2Env,BaseEnv):

    def __init__(self,cfg):
        super(DIStarEnv, self).__init__(cfg)

    def reset(self):
        return super(DIStarEnv,self).reset()

    def close(self):
        super(DIStarEnv,self).close()

    def step(self,actions):
        # 一般BaseEnv返回 ('obs', 'reward', 'done', 'info')
        # 这里DI-star返回 ({'raw_obs': self._obs[agent_idx], 'opponent_obs': opponent_obs, 'action_result': self._action_result[agent_idx]}, reward, episode_complete)
        return super(DIStarEnv,self).step(actions)

    def seed(self, seed, dynamic_seed=False):
        self._random_seed = seed
    
    @property
    def observation_space(self):
        # 作用:
        # 除了限制 observation，以及偶尔提取一些常数外，没看出啥别的用处
        #TODO
        pass

    @property
    def action_space(self):
        # 作用:
        # 1. cfg里用来判断continuous/discrete/hybird, regression/reparameterization/, 和这里的action_space 应该没啥关系
        # 2. test_cql, test_r2d3, test_gail_irl_model 等函数中，是一个整数常数，实际上是action_size/action_shape, 这里可以认为是名词滥用，和真正的space也没啥太大关系
        # 3. IMPORTANT: 被random_collect 调用的 PolicyFactory.get_random_policy, 会使用 action_space 来做sample(), 继承自 gym.space 的 action_space 是可以做sample的
        # 4. 某些环境会定义 ramdom_action 方法，用 action_space 来做 sample, 但是我记得 DI-star 里 gent 也有 random_action, 所以这个可以免掉
        # 5. 某些环境的 step 会使用, 看情况
        # 6. assert限制action

        # 3, 4都是用于拿到random_action的，所以我们只要实现 random_action 的方法, action_space可能也不需要
        # random_action 和 random_collect 给的data(state, action) 在action层面本质上应该是一回事，就看observation是不是有区别了
        #TODO
        pass

    def random_action(self, obs):
        raw = obs[0]['raw_obs'].observation.raw_data

        all_unit_types = set()
        self_unit_types = set()
        
        for u in raw.units:
            # 简单起见我们只选择除了“正在被制造的建筑物”之外的单位
            if u.build_progress == 1:
                all_unit_types.add(u.unit_type)
                if u.alliance == 1:
                    self_unit_types.add(u.unit_type)
        
        avail_actions = [
            {0: {'exist_selected_types':[], 'exist_target_types':[]}}, 
            {168:{'exist_selected_types':[], 'exist_target_types':[]}}
        ] # no_op and raw_move_camera don't have seleted_units 

        for action_id, action in ACTIONS_STAT.items():
            exist_selected_types = list(self_unit_types.intersection(set(action['selected_type'])))
            exist_target_types = list(all_unit_types.intersection(set(action['target_type'])))

            # 如果这个动作是应该有target_type的，但是当前帧不存在有效的target_type，则抛弃该action
            if len(action['target_type']) != 0 and len(exist_target_types) == 0:
                continue

            if len(exist_selected_types) > 0:
                avail_actions.append({action_id: {'exist_selected_types':exist_selected_types, 'exist_target_types':exist_target_types}})
        
        current_action = random.choice(avail_actions)
        func_id, exist_types = current_action.popitem()

        if func_id not in [0, 168]:
            correspond_selected_units = [u.tag for u in raw.units if u.unit_type in exist_types['exist_selected_types'] and u.build_progress == 1]
            correspond_targets = [u.tag for u in raw.units if u.unit_type in exist_types['exist_target_types'] and u.build_progress == 1]

            num_selected_unit = random.randint(0, min(MAX_SELECTED_UNITS_NUM, len(correspond_selected_units)))

            unit_tags =  random.sample(correspond_selected_units, num_selected_unit)
            target_unit_tag = random.choice(correspond_targets) if len(correspond_targets) > 0 else None

        else:
            unit_tags = []
            target_unit_tag = None
            
        data = {
            'func_id': func_id, 
            'skip_steps': random.randint(0, MAX_DELAY - 1),
            # 'skip_steps': 8,
            'queued': random.randint(0, 1),
            'unit_tags': unit_tags, 
            'target_unit_tag': target_unit_tag, 
            'location': (
                random.randint(0, SPATIAL_SIZE[0] - 1),
                random.randint(0, SPATIAL_SIZE[1] - 1)
            )
        }
        return {0:[data]}


    @property
    def reward_space(self):
        # 作用
        # 限制reward的范围，就这一个
        #TODO
        pass

    def __repr__(self):
        return "DI-engine DI-star Env"

# if __name__ == '__main__':
#     no_target_unit_actions = sorted([action['func_id'] for action in ACTIONS if action['target_unit'] == False])
#     no_target_unit_actions_dict = sorted([action_id for action_id, action in ACTIONS_STAT.items() if len(action['target_type']) == 0])
#     print(no_target_unit_actions)
#     print(no_target_unit_actions_dict)
#     assert no_target_unit_actions == no_target_unit_actions_dict
