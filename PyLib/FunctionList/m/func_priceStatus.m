function price_status = func_priceStatus(close_px, len_regression, trend_percent_cut)

slope_px = zeros(length(close_px),1);
for idx=len_regression:length(close_px)
    x = [idx-len_regression+1:idx]';
    y = close_px(x);
    slope_px(idx) = sum((x-mean(x)).*(y-mean(y)))/sum((x-mean(x)).^2);
end 

price_status = zeros(length(close_px),1);
for idx=len_regression:length(close_px)
    percent_temp = length(find(abs(slope_px(1:idx))>abs(slope_px(idx)))) / idx;
    if percent_temp>1-trend_percent_cut
        price_status(idx) = 0;
    else
        price_status(idx) = sign(slope_px(idx));
    end
end


end