function eml_600_direction = func_eml600_direction(eml_600, len_lookback, percent_confirm)

num_data = length(eml_600);

eml_600_direction = zeros(num_data,1);

for idx=len_lookback:num_data
    if length(find( (eml_600(idx)-eml_600(idx-len_lookback+1:idx))>0 )) > len_lookback*percent_confirm
        eml_600_direction(idx) = 1;
    elseif length(find( (eml_600(idx)-eml_600(idx-len_lookback+1:idx))<0 )) > len_lookback*percent_confirm
        eml_600_direction(idx) = -1;
    end
end


end