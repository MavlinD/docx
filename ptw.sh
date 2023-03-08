#!/bin/bash
# стартер для ptw, позволяет менять LOG_LEVEL глобально, на время тестов
# пример: ptw -- 10 mon
# пример с маркером: ptw -- 10 mon only
# echo $1
# echo $2
# echo $3

if [[ $2 == 'mon' ]]; then
  cmd="--picked --testmon --tb=short --no-header"
else
  cmd="--tb=short --no-header"
fi

if [[ $3 ]]; then
    cmd=$cmd' -m '$3
fi

LL=${1:-20}
# echo $LL
# echo $2
# exit
export LOG_LEVEL=$LL
echo $bold $cyan $cmd $nc
pytest $cmd
unset LOG_LEVEL
# echo $yellow"unset LOG_LEVEL"$nc
