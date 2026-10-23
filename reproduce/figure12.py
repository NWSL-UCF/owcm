        .build(distance_m=R, attenuation_c=c, **uw_common)
    ))
    ax.plot(d, y, label=label)
y = powers(d, lambda R: (
    Channel.environment('underwater').defaults('los_link')
    .build(distance_m=R, attenuation_c=0.05, theta0_rad=np.radians(10), **uw_common)
))
ax.plot(d, y, '--', label='LoS Link')
ax.set_title('(c) Underwater: Water Type & Link')
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Received Power (dBm)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# (d) Underwater LoS vs retroreflective
ax = axes[1, 0]
d = np.logspace(np.log10(0.5), np.log10(60), 180)
uw_link_common = dict(
    pt_w=PT_W, wavelength_nm=488.0, DR_m=0.10, DT_m=0.05,
    theta_rad=np.radians(30), etaT=0.9, etaR=0.9,
    attenuation_c=0.20, theta0_rad=np.radians(10),
)
y_los = powers(d, lambda R: (
    Channel.environment('underwater').defaults('los_link')
    .build(distance_m=R, **uw_link_common)
))
y_retro = powers(d, lambda R: (
    Channel.environment('underwater').defaults('retro_link')
    .build(distance_m=R, theta0_retro_rad=0.01, ARetro_m2=0.01,
           etaRetro=0.9, **uw_link_common)
))
ax.semilogx(d, y_los, label='LoS')
ax.semilogx(d, y_retro, label='Retroreflective')
ax.set_title('(d) Underwater: LoS vs Retroreflective')
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Received Power (dBm)')
ax.legend(fontsize=8)
ax.grid(True, which='both', alpha=0.3)

# (e) Underground dust and blockage
ax = axes[1, 1]
d = np.linspace(1, 30, 160)
ug_common = dict(
    pt_w=PT_W, wavelength_nm=550.0, DR_m=0.05, DT_m=0.02,
    dust_conc_mg_m3=0.2, dust_k_per_m_per_mg_m3=0.15,
)
ug_configs = {
    'LoS only': ('none', 'none', 0.0),
    'LoS + Dust': ('exp_extinction', 'none', 0.0),
    'LoS + Dust + Blockage (10%)': ('exp_extinction', 'onoff', 0.1),
    'LoS + Dust + Blockage (30%)': ('exp_extinction', 'onoff', 0.3),
}
for label, (dust, blockage, pb) in ug_configs.items():
    y = powers(d, lambda R, dm=dust, bm=blockage, p=pb: (
        Channel.environment('underground')
        .model('los', 'lambertian_los')
        .model('dust', dm)
        .model('blockage', bm)
        .model('multipath', 'none')
        .build(distance_m=R, p_blocked=p, **ug_common)
    ))
    ax.plot(d, y, label=label)
ax.set_title('(e) Underground: Dust and Blockage Effects')
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Received Power (dBm)')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# (f) Space receiver-aperture scaling using OWCM deep-space link model
ax = axes[1, 2]
d = np.linspace(100, 10000, 200)
for dr in [0.05, 0.10, 0.15, 0.20]:
    y = powers(d, lambda R, D=dr: (
        Channel.environment('space')
        .model('deepspace', 'table_xiii')
        .build(
            distance_m=R, pt_w=PT_W, wavelength_nm=1550.0, DR_m=D,
            w0_rad=0.1, gamma_r=0.0, sigma_p=0.0,
            p0=1.0, La=1.0, Ls=1.0, Lb=1.0, eta_t=0.9, eta_r=0.9,
        )
    ))
    ax.plot(d, y, label=f'DR = {dr*100:.0f}cm')
ax.set_title('(f) Space: Receiver Aperture Gain')
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Received Power (dBm)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig(OUTDIR / 'figure12_owcm_validation.png', dpi=300, bbox_inches='tight')
fig.savefig(OUTDIR / 'figure12_owcm_validation.pdf', dpi=300, bbox_inches='tight')
plt.close(fig)

# Machine-readable record of the principal Figure 12 parameters.
rows = [
    ('Tx Power PT', '0.1 W (~20 dBm)', 'all'),
    ('Wavelength', '1550 nm atmospheric/space; 850 nm indoor; 488-532 nm underwater; 550 nm underground', 'a-f'),
    ('Atmospheric visibility', '2 km', 'a'),
    ('Atmospheric beam divergence', '1 mrad', 'a'),
    ('Underwater extinction c', '0.05, 0.20, 0.40 m^-1', 'c,d'),
    ('Indoor Lambertian order', '1', 'b'),
    ('Indoor FOV', '60 deg half-angle', 'b'),
    ('Indoor reflectivity', '0.7', 'b'),
    ('Indoor blockage probability', '0.4', 'b'),
    ('Underground dust concentration', '0.2 mg/m^3', 'e'),
    ('Underground dust k', '0.15 m^-1 per (mg/m^3)', 'e'),
    ('Underground blockage probability', '0.1, 0.3', 'e'),
    ('Terminal efficiencies', '0.9 where used', 'c,d,f'),
    ('Space receiver diameter', '0.05, 0.10, 0.15, 0.20 m', 'f'),
]
with open(OUTDIR / 'table17_figure12_parameters.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Parameter', 'Value / Description', 'Figure panel'])
    writer.writerows(rows)

print(f'Created {OUTDIR / "figure12_owcm_validation.png"}')
print(f'Created {OUTDIR / "figure12_owcm_validation.pdf"}')
print(f'Created {OUTDIR / "table17_figure12_parameters.csv"}')
