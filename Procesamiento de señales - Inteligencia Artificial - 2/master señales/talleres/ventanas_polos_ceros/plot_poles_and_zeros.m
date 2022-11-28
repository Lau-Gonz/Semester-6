function [] = plot_poles_and_zeros(poles, zeros)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%   INPUT: zeros -> vector de zeros con parte compleja
%          poles -> vector de polos con parte compleja
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


   figure
   hold on 
   grid on 
   if zeros ~= 1
        scatter(real(zeros), imag(zeros), 'bo')
   end
   
   if poles ~= 1 
        scatter(real(poles), imag(poles), 'rx')
   end
   
   title('Ubicación polos y zeros')
   xlabel('Parte real')
   ylabel('Jw')
   hold off
   
end

