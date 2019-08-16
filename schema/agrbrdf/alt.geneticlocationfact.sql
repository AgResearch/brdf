--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: geneticlocationfact_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT geneticlocationfact_obid_key UNIQUE (obid);


--
-- Name: $4; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT "$4" FOREIGN KEY (geneticob) REFERENCES geneticob(obid);


--
-- Name: $5; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT "$5" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


--
-- Name: $6; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT "$6" FOREIGN KEY (genetictestfact) REFERENCES genetictestfact(obid);


--
-- Name: geneticlocationfact_mapobid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY geneticlocationfact
    ADD CONSTRAINT geneticlocationfact_mapobid_fkey FOREIGN KEY (mapobid) REFERENCES biosequenceob(obid);


