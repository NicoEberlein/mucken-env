# MuckenEnv

## Wrappers

### MuckenRLWrapper

This wrapper converts the observation- and info-dict produced by the environment
in such a way that they can be used out-of-the-box for most reinforcement learning algorithms.

The observation dict is converted to a flat vector with shape `(99,)`
The `action_mask` is moved to the info-dict.