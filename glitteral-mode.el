(defvar glitteral-mode-hook nil)

(defun glitteral-insert-def ()
  (interactive)
  (insert ":="))

(defun glitteral-insert-lambda ()
  (interactive)
  (insert "λ"))

(defun glitteral-insert-arrow ()
  (interactive)
  (insert "→"))

(defun glitteral-insert-subtraction-sign ()
  (interactive)
  (insert "−"))

(defun glitteral-insert-multiplication-dot ()
  (interactive)
  (insert "⋅"))

(defun glitteral-insert-division-sign ()
  (interactive)
  (insert "÷"))

(defun glitteral-insert-not-equals ()
  (interactive)
  (insert "≠"))

(defvar glitteral-mode-map
  (let ((map (make-keymap)))
    (define-key map (kbd "M-d") 'glitteral-insert-def)
    (define-key map (kbd "M-l") 'glitteral-insert-lambda)
    (define-key map (kbd "M-*") 'glitteral-insert-multiplication-dot)
    (define-key map [M-kp-divide] 'glitteral-insert-division-sign)
    map)
  "Keymap for Glitteral major mode")

(defconst glitteral-keywords
  '("if" "for" "λ" ":=" ":=λ" "_:="))

(defconst glitteral-font-lock-keywords
  `(("#.*$" 0 font-lock-comment-face)

    (,(concat "(\\("
              (regexp-opt '(":=λ"))
              "\\)\\>"
              ;; whitespace
              "[ \r\n\t]+"
              ;; function name
              "\\([^ \r\n\t()]+\\)")
     (1 font-lock-keyword-face)
     (2 font-lock-function-name-face nil t))

    (,(concat "(\\("
              (regexp-opt '(":=" "_:="))
              "\\)"
              ;; whitespace
              "[ \r\n\t]+"
              ;; variable name
              "\\([^ \r\n\t()]+\\)")
     (1 font-lock-keyword-face)
     (2 font-lock-variable-name-face))

    (,(concat "\\<" (regexp-opt '("Truth" "Falsity" "Void")) "\\>")
     0 font-lock-constant-face)

    (,(concat "\\<" (regexp-opt '("for" "if" "while" "do")) "\\>")
     0 font-lock-keyword-face)

    ("\\^int" 0 font-lock-type-face)
    ("\\^str" 0 font-lock-type-face)
    ("\\^bool" 0 font-lock-type-face)
    ("\\^\\[int\\]" 0 font-lock-type-face)
    ("\\^\\[str\\]" 0 font-lock-type-face)
    ("\\^\\[bool\\]" 0 font-lock-type-face)))

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.gltrl\\'" . glitteral-mode))

(defun glitteral-mode ()
  "Major mode for editing Glitteral source code"
  (interactive)
  (kill-all-local-variables)
  (use-local-map glitteral-mode-map)

  (setq font-lock-defaults '(glitteral-font-lock-keywords))
  (setq-local comment-start-skip "#+\\s-*")
  (setq-local comment-start "#")

  (setq-local indent-line-function 'lisp-indent-line)
  (setq-local lisp-indent-offset 3)

  (setq major-mode 'glitteral-mode)
  (setq mode-name "Glitteral")
  (run-hooks 'glitteral-mode-hook))

(provide 'glitteral-mode)
