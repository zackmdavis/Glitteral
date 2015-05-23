(defvar glitteral-mode-hook nil)

(defun glitteral-insert-lambda ()
  (interactive)
  (insert "λ"))

(defun glitteral-insert-multiplication-dot ()
  (interactive)
  (insert "⋅"))

(defun glitteral-insert-def ()
  (interactive)
  (insert ":="))

(defvar glitteral-mode-map
  (let ((map (make-keymap)))
    (define-key map (kbd "M-d") 'glitteral-insert-def)
    (define-key map (kbd "M-l") 'glitteral-insert-lambda)
    (define-key map (kbd "M-*") 'glitteral-insert-multiplication-dot)
    map)
  "Keymap for Glitteral major mode")

(defconst glitteral-keywords
  '("if" "for" "λ" ":=" ":=λ" "_:="))

(defconst glitteral-font-lock-keywords
  `((,(concat "(\\("
              (regexp-opt '(":=λ"))
              "\\)\\>"
              ;; whitespace
              "[ \r\n\t]+"
              ;; function name
              "\\([^ \r\n\t()]+\\)")
     (1 font-lock-keyword-face)
     (2 font-lock-function-name-face nil t))

   ("\\<int\\>" 0 font-lock-type-face)
   ("\\<str\\>" 0 font-lock-type-face)

   ("\\<for\\>" 0 font-lock-keyword-face)
   ("\\<if\\>" 0 font-lock-keyword-face)))

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.gltrl\\'" . glitteral-mode))

(defun glitteral-mode ()
  "Major mode for editing Glitteral source code"
  (interactive)
  (kill-all-local-variables)
  (use-local-map glitteral-mode-map)
  (setq font-lock-defaults '(glitteral-font-lock-keywords))
  (setq major-mode 'glitteral-mode)
  (setq mode-name "Glitteral")
  (run-hooks 'glitteral-mode-hook))

(provide 'glitteral-mode)
