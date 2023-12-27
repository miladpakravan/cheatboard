# Install and config tmux and tmux resuurect

tmux resurrect is a plugin for save and restore tmux sessions after reboot.

## Install tmux
```
sudo apt install -y tmux
```

## Download tmux resurrect

```
cd ~
git clone https://github.com/tmux-plugins/tmux-resurrect
mv tmux-resurrect .tmux-resurrect
```

## Configure tmux

copy this lines to **~/.tmux.conf**

```
set -g pane-border-status top
# hold arows for resize pane
bind-key -r -T prefix       M-Up              resize-pane -U 5
bind-key -r -T prefix       M-Down            resize-pane -D 5
bind-key -r -T prefix       M-Left            resize-pane -L 5
bind-key -r -T prefix       M-Right           resize-pane -R 5
bind-key -r -T prefix       C-Up              resize-pane -U
bind-key -r -T prefix       C-Down            resize-pane -D
bind-key -r -T prefix       C-Left            resize-pane -L
bind-key -r -T prefix       C-Right           resize-pane -R
set -g repeat-time 1000
run-shell ~/.tmux-resurrect/resurrect.tmux
```

## Save tmux session

After execute **tmux** command, press **CTRL + B** and then press **CTRL + S**

## Restore tmux session

After execute **tmux** command, press **CTRL + B** and then press **CTRL + R**

