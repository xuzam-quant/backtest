function [eml_turn_30, eml_crossover_30] = func_eml_execution_v2(eml_HP200_30, eml_HP1000_30, pos_minmax_30)

eml_turn_30      = zeros(length(eml_HP200_30),1);
eml_crossover_30 = zeros(length(eml_HP200_30),1);

len_lookback_pos_minmax = 20;

eml_HP200_30_direction = [ 0; sign(eml_HP200_30(2:end)-eml_HP200_30(1:end-1))];
status_trigger = 0;
pos_trigger = 1;
for t=len_lookback_pos_minmax:length(eml_HP200_30)    
    idx_temp = find(pos_minmax_30(t-len_lookback_pos_minmax+1:t)~=0,1,'last');
    if ~isempty(idx_temp)
        if pos_minmax_30(t-len_lookback_pos_minmax+1+idx_temp-1)==-1
            status_trigger = -1;
            pos_trigger = t-len_lookback_pos_minmax+1+idx_temp-1;
        elseif pos_minmax_30(t-len_lookback_pos_minmax+1+idx_temp-1)==1
            status_trigger = 1;
            pos_trigger = t-len_lookback_pos_minmax+1+idx_temp-1;
        end
    end        
    if     status_trigger==1        
        if eml_HP200_30_direction(t)==-1  % && any(eml_HP200_30_direction(pos_trigger:t)==-1) && any(eml_HP200_30_direction(pos_trigger:t)==1)
            eml_turn_30(t) = 1;
            status_trigger = 0;
        end                             
    elseif status_trigger==-1
        if  eml_HP200_30_direction(t)==1  % && any(eml_HP200_30_direction(pos_trigger:t)==-1) && any(eml_HP200_30_direction(pos_trigger:t)==1)
            eml_turn_30(t) = -1;
            status_trigger = 0;
        end       
    end                
end

t_crossover_exist = 0;
for t=2:length(eml_HP200_30)
    if     eml_HP200_30(t)>eml_HP1000_30(t) && eml_HP200_30(t-1)<eml_HP1000_30(t-1)
        eml_crossover_30(t:min(t+t_crossover_exist,length(eml_HP200_30))) = 1;
    elseif eml_HP200_30(t)<eml_HP1000_30(t) && eml_HP200_30(t-1)>eml_HP1000_30(t-1)
        eml_crossover_30(t:min(t+t_crossover_exist,length(eml_HP200_30))) = -1;
    end        
end


end