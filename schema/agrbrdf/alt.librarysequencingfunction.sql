--
-- Name: obid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN obid SET DEFAULT nextval(('ob_obidseq'::text)::regclass);


--
-- Name: obtypeid; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN obtypeid SET DEFAULT 0;


--
-- Name: createddate; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN createddate SET DEFAULT now();


--
-- Name: checkedout; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN checkedout SET DEFAULT false;


--
-- Name: statuscode; Type: DEFAULT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction ALTER COLUMN statuscode SET DEFAULT 1;


--
-- Name: librarysequencingfunction_obid_key; Type: CONSTRAINT; Schema: public; Owner: agrbrdf; Tablespace: 
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_obid_key UNIQUE (obid);


--
-- Name: librarysequencingfunction_biolibraryob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_biolibraryob_fkey FOREIGN KEY (biolibraryob) REFERENCES biolibraryob(obid);


--
-- Name: librarysequencingfunction_bioprotocolob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_bioprotocolob_fkey FOREIGN KEY (bioprotocolob) REFERENCES bioprotocolob(obid);


--
-- Name: librarysequencingfunction_datasourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_datasourceob_fkey FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: librarysequencingfunction_labresourcelist_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_labresourcelist_fkey FOREIGN KEY (labresourcelist) REFERENCES labresourcelist(obid);


--
-- Name: librarysequencingfunction_labresourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY librarysequencingfunction
    ADD CONSTRAINT librarysequencingfunction_labresourceob_fkey FOREIGN KEY (labresourceob) REFERENCES labresourceob(obid);


