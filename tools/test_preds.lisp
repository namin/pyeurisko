(defunit pred
  worth 500
  isa (category anything repr-concept)
  examples (unary-pred binary-pred tertiary-pred))

(defunit unary-pred
  worth 500
  higher-arity (binary-pred)
  generalizations (unary-op pred op anything)
  isa (repr-concept anything category pred-cat-by-nargs op-cat-by-nargs)
  examples (always-t always-nil constant-unary-pred undefined-pred not)
  fast-defn (lambda (f)
              (let ((r (and (memb 'pred (isa f))
                            (eq 1 (arity f)))))
                (cprin1 99 "unary-pred called for " f " with result " r "~%")
                r))
  rarity (0.1182796 11 82))

(defunit binary-pred
  worth 500
  lower-arity (unary-pred)
  higher-arity (tertiary-pred)
  generalizations (binary-op pred op anything)
  isa (repr-concept anything category pred-cat-by-nargs op-cat-by-nargs)
  examples (equal ieqp eq ileq igeq ilessp igreaterp and or the-second-of
                  the-first-of struc-equal set-equal subsetp constant-binary-pred
                  always-t-2 always-nil-2 o-set-equal bag-equal list-equal member memb
                  implies)
  fast-defn (lambda (f)
              (and (memb 'pred (isa f))
                   (eq 2 (arity f))))
  int-examples (ieqp eq struc-equal set-equal o-set-equal bag-equal list-equal memb member)
  rarity (0.07526882 7 86))

(defunit tertiary-pred
  lower-arity (binary-pred)
  worth 500
  generalizations (tertiary-op pred op anything)
  isa (repr-concept anything category pred-cat-by-nargs op-cat-by-nargs)
  fast-defn (lambda (f)
              (and (memb 'pred (isa f))
                   (eq 3 (arity f))))
  rarity (0.1827957 17 76))