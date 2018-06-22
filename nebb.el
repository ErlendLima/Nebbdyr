;; simple major mode, nebbdyr-mode


(setq nebbdyr-font-lock-keywords
      (let* (
            ;; define several category of keywords
             (x-keywords '("break" "while" "in" ".." "for" "unstable" "continue" "else" "print"
                           "if" "fun" "return" "ensure" "mut" "var" "class"))

            ;; generate regex string for each category of keywords
            (x-keywords-regexp (regexp-opt x-keywords 'words)))

        `(
          (,x-keywords-regexp . font-lock-keyword-face)
          ;; note: order above matters, because once colored, that part won't change.
          ;; in general, put longer words first
          )))

;;;###autoload
(define-derived-mode nebbdyr-mode python-mode "nebbdyr mode"
  "Major mode for editing Nebbdyr"
  (setq font-lock-defaults '((nebbdyr-font-lock-keywords))))

(provide 'nebbdyr-mode)
