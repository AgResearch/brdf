--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: sequencingfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT sequencingfunction_obid_key UNIQUE (obid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT "$2" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


--
-- Name: $3; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT "$3" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT "$4" FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT "$5" FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


--
-- Name: sequencingfunction_biolibraryob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY sequencingfunction
    ADD CONSTRAINT sequencingfunction_biolibraryob_fkey FOREIGN KEY (biolibraryob) REFERENCES biolibraryob(obid);


