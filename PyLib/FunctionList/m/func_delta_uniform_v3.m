function [eml_delta, price_delta] = func_delta_uniform_v3(eml_HP1000_30, close_30, len_delta_min, len_lookback, cut_eml_bounce_highlow)

eml_delta   = zeros(length(eml_HP1000_30),2);
price_delta = zeros(length(eml_HP1000_30),2);

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
        if eml_HP1000_30(idx-len_lookback_delta) - val_max_min2min < -cut_eml_bounce_highlow && all(pos_minmax_raw(idx-len_nearby_pass+1:idx,1)~=-1)
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
        if eml_HP1000_30(idx-len_lookback_delta) - val_min_max2max > cut_eml_bounce_highlow && all(pos_minmax_raw(idx-len_nearby_pass+1:idx,1)~=1)
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

len_nearby = 5;
status_up_down=0;
pos_up_down=1;
for idx=len_delta_min:length(eml_HP1000_30)
    if pos_minmax_raw(idx,1)==-1
        status_up_down=-1;
        pos_up_down = idx;
    elseif pos_minmax_raw(idx,1)==1
        status_up_down=1;
        pos_up_down = idx;
    end
    
    if status_up_down==-1
        eml_delta(idx,1) = 1;
        eml_delta(idx,2) = eml_HP1000_30(idx) - eml_HP1000_30(pos_minmax_raw(pos_up_down,2));
        price_delta(idx,1) = 1;
        price_delta(idx,2) = close_30(idx) / min(close_30(pos_minmax_raw(pos_up_down,2)-len_nearby+1:pos_minmax_raw(pos_up_down,2))) - 1;        
    elseif status_up_down==1
        eml_delta(idx,1) = -1;
        eml_delta(idx,2) = eml_HP1000_30(idx) - eml_HP1000_30(pos_minmax_raw(pos_up_down,2));
        price_delta(idx,1) = -1;
        price_delta(idx,2) = close_30(idx) / max(close_30(pos_minmax_raw(pos_up_down,2)-len_nearby+1:pos_minmax_raw(pos_up_down,2))) - 1;        
    end
    
    
end





end