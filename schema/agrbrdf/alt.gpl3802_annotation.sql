--
-- Name: gpl3802_annotation_datasourceob_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gpl3802_annotation
    ADD CONSTRAINT gpl3802_annotation_datasourceob_fkey FOREIGN KEY (datasourceob) REFERENCES datasourceob(obid);


--
-- Name: gpl3802_annotation_voptypeid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY gpl3802_annotation
    ADD CONSTRAINT gpl3802_annotation_voptypeid_fkey FOREIGN KEY (voptypeid) REFERENCES obtype(obtypeid);


