L = 180000; %Longitud de la señal
T = 30;     %Duración de la señal
Fs = L/T;   %Frecuencia de muestreo

%vector entre 0 y 1/2 multiplicado por Fs
%vector entre 0 y Fs/2
f = Fs*(0:L/2)/L;

%vector de tiempo de 10000 elementos
t = linspace(0, T, L);
y = sin(2*pi*t);        %señal sinusoidal
w = f*2*pi;             %vector omega, de frecuencias angulares
epsilon = 0.00000000001;

dist_max = 600;
realPart1 = [ log(linspace(0, dist_max, 20) + epsilon) ]; 
zeros1 = [ linspace(0, dist_max, 20)*2*pi ].*1i - realPart1; 

H_H1 = high_pass_win(w, 1, zeros1);
plot_all_about_win(f, t, H_H1);

%% Hechura del pasabajas

realPart2 = [ log(linspace(3000-dist_max, 3000, 30) + epsilon) ]; 
zeros2 = [ linspace(3000-dist_max, 3000, 30)*2*pi ].*1i %- realPart2; 

H_H2 = high_pass_win(w, 1, zeros2);
plot_all_about_win(f, t, H_H2);

%% Filtro pasa bandas

H_H = (H_H1.*H_H2);
H_H = H_H./max(abs(H_H));
plot_all_about_win(f, t, H_H);

