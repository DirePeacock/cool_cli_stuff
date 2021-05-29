(require 'package)

;;(setq package-enable-at-startup nil)
(add-to-list 'package-archives 
             '("melpa" . "https://melpa.org/packages/") t)

(add-to-list 'package-archives 
             '("gnu" . "https://elpa.gnu.org/packages/") t)

(add-to-list 'package-archives (cons "melpa" (concat proto "://melpa.org/packages/")) t)

;;(package-initialize)
(setq initial-buffer-choice `eshell)
(load-theme 'misterioso)
(scroll-bar-mode -1)
(tool-bar-mode -1)

(defalias 'yes-or-no-p 'y-or-n-p)

(setq find-program "c:/Git/usr/bin/find.exe")

(setq python-shell-interpreter "c:/Python39/Scripts/ipython.exe")
(when (fboundp 'windmove-default-keybindings)
  (windmove-default-keybindings))
