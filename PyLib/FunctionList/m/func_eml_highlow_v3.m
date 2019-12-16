function [eml_highlow, eml1000_percentile, eml200_percentile] = func_eml_highlow_v3(eml_HP1000_30,eml_HP200_30, len_lookback, len_lookback_2, cut_eml_bounce_highlow)

cut_percent_delta  = 0.65;
len_lookback_delta = 6;
len_nearby_pass    = 20;
pos_minmax_raw          = zeros(length(eml_HP1000_30),2);
pos_minmax_last_valid   = ones(length(eml_HP1000_30),2);
status_min_init  = 0;
status_max_init  = 0;
idx_last_min_raw = 1;
idx_last_max_raw = 1;
for idx=2*len_lookback_delta+1:length(eml_HP1000_30)
    pos_minmax_last_valid(idx,1) = pos_minmax_last_valid(idx-1,1);
    pos_minmax_last_valid(idx,2) = pos_minmax_last_valid(idx-1,2);
    
    delta_left  = eml_HP1000_30(idx-len_lookback_delta) - eml_HP1000_30(idx-2*len_lookback_delta:idx-len_lookback_delta-1);
    delta_right = eml_HP1000_30(idx-len_lookback_delta) - eml_HP1000_30(idx-len_lookback_delta+1:idx);
    
    %update raw minmax
    if     length(find(delta_left<0))  > len_lookback_delta*cut_percent_delta ...  %local min
        && length(find(delta_right<0)) > len_lookback_delta*cut_percent_delta   
        if status_min_init==0 || status_max_init==0
            pos_minmax_last_valid(idx,1) = idx-len_lookback_delta;
            status_min_init=1;
            pos_minmax_raw(idx,1) = -1;  
            pos_minmax_raw(idx,2) = idx-len_lookback_delta;        
            continue;
        end        
        %if down enough to be a valid min
        %if eml_HP1000_30(idx-len_lookback_delta) - eml_HP1000_30(pos_minmax_last_valid(idx,2)) < -cut_eml_bounce_highlow && all(pos_minmax_raw(idx-len_nearby_pass+1:idx,1)~=-1)
        %idx_last_max = find(pos_minmax_raw(1:idx)==1,1,'last');
        %if eml_HP1000_30(idx-len_lookback_delta) - eml_HP1000_30(pos_minmax_raw(idx_last_max,2)) < -cut_eml_bounce_highlow && all(pos_minmax_raw(idx-len_nearby_pass+1:idx,1)~=-1)
        [val_max_min2min, pos_max_min2min] = max(eml_HP1000_30(pos_minmax_last_valid(idx,1):idx-len_lookback_delta));
        pos_max_min2min = pos_max_min2min + pos_minmax_last_valid(idx,1) - 1;
        if min(eml_HP1000_30(pos_max_min2min:idx-len_lookback_delta)) < eml_HP1000_30(idx-len_lookback_delta)
            continue;
        end
        if eml_HP1000_30(idx-len_lookback_delta) - max(eml_HP1000_30(pos_minmax_last_valid(idx,1):idx-len_lookback_delta)) < -cut_eml_bounce_highlow && all(pos_minmax_raw(idx-len_nearby_pass+1:idx,1)~=-1)
            pos_minmax_raw(idx,1) = -1;  
            pos_minmax_raw(idx,2) = idx-len_lookback_delta;        
            idx_last_min_raw = idx-len_lookback_delta; 
        end                        
    elseif length(find(delta_left>0))  > len_lookback_delta*cut_percent_delta ... %local max
        && length(find(delta_right>0)) > len_lookback_delta*cut_percent_delta        
        if status_min_init==0 || status_max_init==0
            pos_minmax_last_valid(idx,2) = idx-len_lookback_delta;
            status_max_init=1;
            pos_minmax_raw(idx,1) = 1;  
            pos_minmax_raw(idx,2) = idx-len_lookback_delta;        
            continue;
        end    
        %if up enough to be a valid max        
        %if eml_HP1000_30(idx-len_lookback_delta) - eml_HP1000_30(pos_minmax_last_valid(idx,1)) > cut_eml_bounce_highlow && all(pos_minmax_raw(idx-len_nearby_pass+1:idx,1)~=1)
        %idx_last_min = find(pos_minmax_raw(1:idx)==-1,1,'last');
        %if eml_HP1000_30(idx-len_lookback_delta) - eml_HP1000_30(pos_minmax_raw(idx_last_min,2)) > cut_eml_bounce_highlow && all(pos_minmax_raw(idx-len_nearby_pass+1:idx,1)~=1)        
        [val_min_max2max, pos_min_max2max] = min(eml_HP1000_30(pos_minmax_last_valid(idx,2):idx-len_lookback_delta));
        pos_min_max2max = pos_min_max2max + pos_minmax_last_valid(idx,2) - 1;
        if max(eml_HP1000_30(pos_min_max2max:idx-len_lookback_delta)) > eml_HP1000_30(idx-len_lookback_delta)
            continue;
        end
        if eml_HP1000_30(idx-len_lookback_delta) - min(eml_HP1000_30(pos_minmax_last_valid(idx,2):idx-len_lookback_delta)) > cut_eml_bounce_highlow && all(pos_minmax_raw(idx-len_nearby_pass+1:idx,1)~=1)
            pos_minmax_raw(idx,1) = 1;  
            pos_minmax_raw(idx,2) = idx-len_lookback_delta;        
            idx_last_max_raw = idx-len_lookback_delta; 
        end
    end
    
    %update last valid minmax
    if pos_minmax_last_valid(idx,1)~=idx_last_min_raw
        if eml_HP1000_30(idx) - eml_HP1000_30(idx_last_min_raw) > cut_eml_bounce_highlow
            pos_minmax_last_valid(idx,1) = idx_last_min_raw;
        end
    end
    if pos_minmax_last_valid(idx,2)~=idx_last_max_raw
        if eml_HP1000_30(idx) - eml_HP1000_30(idx_last_max_raw) < -cut_eml_bounce_highlow
            pos_minmax_last_valid(idx,2) = idx_last_max_raw;
        end
    end        
end


len_nearby     = 10;
eml_highlow    = zeros(length(eml_HP1000_30),2);
eml1000_percentile = zeros(length(eml_HP1000_30),1);
eml200_percentile  = zeros(length(eml_HP1000_30),1);
for idx=len_lookback:length(eml_HP1000_30) 
    
    pos_min_last_valid = unique(pos_minmax_last_valid(idx-len_lookback+1:idx,1));
    pos_max_last_valid = unique(pos_minmax_last_valid(idx-len_lookback+1:idx,2));
    
    eml_highlow(idx,1) = mean(eml_HP1000_30(pos_min_last_valid));
    eml_highlow(idx,2) = mean(eml_HP1000_30(pos_max_last_valid)); 
    if eml_highlow(idx,2)-eml_highlow(idx,1)~=0
        eml1000_percentile(idx,1) = (eml_HP1000_30(idx)-eml_highlow(idx,1)) / (eml_highlow(idx,2) - eml_highlow(idx,1));
        eml200_percentile(idx,1)  = (eml_HP200_30(idx)-eml_highlow(idx,1)) / (eml_highlow(idx,2) - eml_highlow(idx,1));
    else 
        eml1000_percentile(idx,1) = eml1000_percentile(idx-1,1);
        eml200_percentile(idx,1) = eml200_percentile(idx-1,1);
    end    
end



end