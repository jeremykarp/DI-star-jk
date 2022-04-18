from distar.envs.env import SC2Env

from ding.envs import BaseEnv

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

    @property
    def reward_space(self):
        # 作用
        # 限制reward的范围，就这一个
        #TODO
        pass

    def __repr__(self):
        return "DI-engine DI-star Env"