(defvar glitteral-mode-hook nil)

(defun glitteral-insert-def ()
  (interactive)
  (insert ":="))

(defun glitteral-insert-lambda ()
  (interactive)
  (insert "λ"))  ; \u03BB

(defun glitteral-insert-dash ()
  (interactive)
  (insert "—"))  ; \u2014

(defun glitteral-insert-arrow ()
  (interactive)
  (insert "→"))  ; \u2192

(defun glitteral-insert-subtraction ()
  (interactive)
  (insert "−"))  ; \u2212

(defun glitteral-insert-multiplication ()
  (interactive)
  (insert "⋅"))  ; \u22C5

(defun glitteral-insert-division ()
  (interactive)
  (insert "÷"))  ; \u00F7

(defun glitteral-insert-not-equals ()
  (interactive)
  (insert "≠"))  ; \u2260

(defun glitteral-insert-ellipsis ()
  (interactive)
  (insert "…"))  ; \u2026


(defvar glitteral-mode-map
  (let ((map (make-keymap)))
    (define-key map (kbd "M-d") 'glitteral-insert-def)
    (define-key map (kbd "M-l") 'glitteral-insert-lambda)
    (define-key map (kbd "M-_") 'glitteral-insert-dash)
    (define-key map [M-kp-subtract] 'glitteral-insert-subtraction)
    (define-key map (kbd "M-*") 'glitteral-insert-multiplication)
    (define-key map [M-kp-divide] 'glitteral-insert-division)
    (define-key map (kbd "M-.") 'glitteral-insert-ellipsis)
    map)
  "Keymap for Glitteral major mode")

(defconst glitteral-indentation-width 3)

(defconst glitteral-font-lock-keywords
  `(("#.*$" 0 font-lock-comment-face)

    (,(concat "\\("
              (regexp-opt '(":=λ"))
              "\\)\\>"
              ;; whitespace
              "[ \r\n\t]+"
              ;; function name
              "\\([^ \r\n\t()]+\\)")
     (1 font-lock-keyword-face)
     (2 font-lock-function-name-face nil t))

    (,(concat "\\("
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

    (,(concat "\\<" (regexp-opt '("for" "if" "while" "do" "when")) "\\>")
     0 font-lock-keyword-face)

    ;; XXX TODO FIXME: "=" and "append!" don't seem to work?!
    (,(concat "\\<" (regexp-opt '("append!" "length" "=" "greater?" "less?"
                                  "not_greater?" "not_less?" "range" "print"
                                  "println" "input" "and" "or" "λ")) "\\>")
     0 font-lock-builtin-face)

    ("\\^int" 0 font-lock-type-face)
    ("\\^float" 0 font-lock-type-face)
    ("\\^str" 0 font-lock-type-face)
    ("\\^bool" 0 font-lock-type-face)
    ("\\^\\[int\\]" 0 font-lock-type-face)
    ("\\^\\[str\\]" 0 font-lock-type-face)
    ("\\^\\[bool\\]" 0 font-lock-type-face)))

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.gltrl\\'" . glitteral-mode))

(defun glitteral-get-line-indentation-level ()
  (interactive)
  (save-excursion
    (move-beginning-of-line nil)
    (re-search-forward "[^\s-]")
    (backward-char)
    (/ (current-column) glitteral-indentation-width)))

(defun glitteral-set-line-indentation-level (level)
  (save-excursion
    (move-beginning-of-line nil)
    (let ((start-of-line (point)))
      (re-search-forward "[^\s-]")
      (backward-char)
      (delete-region start-of-line (point)))
    (insert-char ?  (* glitteral-indentation-width level)))
  (re-search-forward "[^\s-]")
  (backward-char))

(defun glitteral-indent-line ()
  ;; TODO: detect if point is delimited, use different rule in that case
  (interactive)
  (let* ((previous-indent (save-excursion
                            (previous-line)
                            (glitteral-get-line-indentation-level)))
         (current-indent (glitteral-get-line-indentation-level)))
    (if (> current-indent previous-indent)
        (glitteral-set-line-indentation-level 0)
      (glitteral-set-line-indentation-level (1+ current-indent)))))

;;;###autoload
(define-derived-mode glitteral-mode prog-mode "Glitteral"
  "Major mode for editing Glitteral source code"
  (use-local-map glitteral-mode-map)

  (setq font-lock-defaults '(glitteral-font-lock-keywords))
  (setq-local comment-start-skip "#+\\s-*")
  (setq-local comment-start "#")

  (setq-local indent-line-function 'glitteral-indent-line)

  (setq mode-name "Glitteral")
  (setq major-mode 'glitteral-mode)

  (run-hooks 'glitteral-mode-hook))

(provide 'glitteral-mode)
