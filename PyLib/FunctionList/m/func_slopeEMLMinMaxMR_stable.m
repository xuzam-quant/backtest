function [pos_minmax, slope_eml] = func_slopeEMLMinMaxMR_stable(eml, cut_eml, level_high, len_slp, len_build_data)
%{
Description:
    Function used to get the turning point for the input time series, mainly for emotion line.
	Example: time series would be like, [0,0,0,0,-1,0,0¡­0,0,1,0,0¡­]. 
             -1 represents min point. 1 represents max point.
Inputs:
	Eml:            emotion line time series, size is (n,1).
    EmlCut:         band cut for big emotion line value. (high eml region, recommend 30) 
    levelHigh:      band cut for big slope level value. (Max slope level is 14). 
                    Can use 14(enable this turn point search method) or 15(disable this search method).
    len_slp:        length of slope calculation lookback period. 
                    For em200(1min), use 100;  For em1000(1min), use 450.
Outputs:
    pos_minmax:     min/max point time series. Size is (n,1).
    slope:          emotion line slope discretization value(1,2,4,6¡­). Size is (n,1).
    slopeEml:       some slope value, 1 column is slope true value, 
                    1 column is slope discretization value. Usually don¡¯t use this. Size is (n,2). 
%}

numEml      = length(eml);
slope_eml   = zeros(numEml,2);  %level,value
pos_minmax  = zeros(numEml,1);

% 1.1 get Eml slope value
bound_slp   = 0.01;
for i=len_slp:numEml
    [slope_eml(i,2), slope_eml(i,1)] = func_slope(eml(i-len_slp+1:i), len_slp, bound_slp);
end

% 1.2 get recommended bound and slope level
CI_EmlSlp       = 0.25;   % make 75% EmlSlope below about level 6.5.
level_EmlSlp    = 6.5;

bound_slp = ones(numEml,1) * 0.01;
for i=len_build_data:numEml
    LH_EmlSlp    = icdf('normal',[CI_EmlSlp/2 1-CI_EmlSlp/2], mean(slope_eml(i-len_build_data+1:i,1)), std(slope_eml(i-len_build_data+1:i,1)) );    
    bound_slp(i) = mean(abs(LH_EmlSlp)) / level_EmlSlp;
end
for i=len_build_data:numEml
    slope_eml(i,2)  = func_boundLevel(slope_eml(i,1), bound_slp(i));
end

% 2. get Eml minmax position. 1_max, -1_min, 0_none
%    2-type search: (1)When Eml slope high, get position when slope&Eml both high
%                   (2)When Eml slope low,  get Eml slope turn point.                  
levelTurn   = 2;
levelDouble = 4;
len_EmlLook = round(len_slp/5);

slope       = slope_eml(:,2);
statusFind  = zeros(length(slope),1);
last_status = 0;
for i=max(len_EmlLook,len_build_data):numEml
    statusFind(i) = statusFind(i-1);
    %-------------   min position   -------------%
    if slope(i)<=-levelTurn && statusFind(i)~=-1
        % 1. slope negative and turn up
        if slope(i)>slope(i-1) && statusFind(i)~=-1
            statusFind(i) = -1;
            pos_minmax(i) = -1;
        end  
        % 2. slope break high and eml in high band
        if slope(i)<=-level_high && statusFind(i)~=-1 && eml(i)<-cut_eml       
            statusFind(i) = -1;
            pos_minmax(i) = -1;
        end          
        % 3. slope flat and hold for a while, no need to wait it turn.
        if min(slope(i-len_EmlLook+1:i))==max(slope(i-len_EmlLook+1:i)) && statusFind(i)~=-1
            if eml(i) > min(eml(i-len_EmlLook+1:i)) 
                statusFind(i) = -1;
                pos_minmax(i) = -1;
            end
        end        
    end
    
    % reset status, when already find a min pos, slope positive, eml turn up
    if statusFind(i)==-1 && slope(i)>=0 && eml(i)>eml(i-1)
        last_status = -1;
        statusFind(i) = 0;
    end
    if statusFind(i)==-1 && slope(i)<0 && slope(i)>-level_high && eml(i)<eml(i-1) && slope(i)<slope(i-1)
        last_status = -1;
        statusFind(i) = 1;
        pos_minmax(i) = 1;
    end
    if statusFind(i)==0 && slope(i)<0 && slope(i)>-level_high && eml(i)<eml(i-1) && slope(i)<slope(i-1) && last_status==-1       
        last_status = -1;
        statusFind(i) = 1;
        pos_minmax(i) = 1;
    end
%     if statusFind(i)==0 && slope(i)==0 && all(Eml(i-29:i)-Eml(i-30:i-1)<0) && last_status==-1       
%         last_status = -1;
%         statusFind(i) = 1;
%         pos_minmax(i) = 1;
%     end

       
    
    %-------------   max position   -------------%
    if slope(i)>=levelTurn && statusFind(i)~=1
        % 1. slope positive and turn down
        if slope(i)<slope(i-1) && statusFind(i)~=1 
            statusFind(i) = 1;
            pos_minmax(i) = 1;
        end
        % 2. slope break high and eml in high band
        if slope(i)>=level_high && statusFind(i)~=1 && eml(i)>cut_eml       
            statusFind(i) = 1;
            pos_minmax(i) = 1;
        end
        % 3. slope flat and hold for a while, no need to wait it turn.
        if min(slope(i-len_EmlLook+1:i))==max(slope(i-len_EmlLook+1:i)) && statusFind(i)~=1
            if eml(i) < max(eml(i-len_EmlLook+1:i))
                statusFind(i) = 1;
                pos_minmax(i) = 1;
            end
        end        
    end
    
    % reset status, when already find a max pos, slope negative, eml turn down
    if statusFind(i)==1 && slope(i)<=0 && eml(i)<eml(i-1)
        last_status = 1;
        statusFind(i) = 0;
    end
    if statusFind(i)==1 && slope(i)>0 && slope(i)<level_high && eml(i)>eml(i-1) && slope(i)>slope(i-1)
        last_status = 1;
        statusFind(i) = -1;
        pos_minmax(i) = -1;
    end
    if statusFind(i)==0 && slope(i)>0 && slope(i)<level_high && eml(i)>eml(i-1) && slope(i)>slope(i-1) && last_status==1
        last_status = 1;
        statusFind(i) = -1;
        pos_minmax(i) = -1;
    end
%     if statusFind(i)==0 && slope(i)==0 && all(Eml(i-9:i)-Eml(i-10:i-1)>0) && last_status==1       
%         last_status = 1;
%         statusFind(i) = -1;
%         pos_minmax(i) = -1;
%     end

end

end


function [slope_level, slope_value] = func_slope(Eml, len_slp, bound)

y = Eml;
sizeY = size(y);
x = zeros(sizeY(1),sizeY(2));
x(1:end) = 1:len_slp;

diff1st = sum((x-mean(x)).*(y-mean(y)))/sum((x-mean(x)).^2);
slope_value = diff1st;
diff1st = 1*(diff1st>bound) + ...
    1*(diff1st>(2*bound)) + ...
    2*(diff1st>(4*bound)) + ...
    2*(diff1st>(6*bound)) + ...
    2*(diff1st>(8*bound)) + ...
    2*(diff1st>(10*bound)) + ...
    2*(diff1st>(12*bound)) + ...
    2*(diff1st>(14*bound)) - ...
    1*(diff1st<-bound) - ...
    1*(diff1st<(-2*bound)) - ...
    2*(diff1st<(-4*bound)) - ...
    2*(diff1st<(-6*bound)) - ...
    2*(diff1st<(-8*bound)) - ...
    2*(diff1st<(-10*bound)) - ...
    2*(diff1st<(-12*bound)) - ...
    2*(diff1st<(-14*bound));
slope_level = diff1st;
end


function slope_level = func_boundLevel(slope_value,bound)
diff1st = slope_value;
diff1st = 1*(diff1st>bound) + ...
    1*(diff1st>(2*bound)) + ...
    2*(diff1st>(4*bound)) + ...
    2*(diff1st>(6*bound)) + ...
    2*(diff1st>(8*bound)) + ...
    2*(diff1st>(10*bound)) + ...
    2*(diff1st>(12*bound)) + ...
    2*(diff1st>(14*bound)) - ...
    1*(diff1st<-bound) - ...
    1*(diff1st<(-2*bound)) - ...
    2*(diff1st<(-4*bound)) - ...
    2*(diff1st<(-6*bound)) - ...
    2*(diff1st<(-8*bound)) - ...
    2*(diff1st<(-10*bound)) - ...
    2*(diff1st<(-12*bound)) - ...
    2*(diff1st<(-14*bound));
slope_level = diff1st;
end
