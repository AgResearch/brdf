--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY obtypesignature
    ADD CONSTRAINT "$1" FOREIGN KEY (obtypeid) REFERENCES obtype(obtypeid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY obtypesignature
    ADD CONSTRAINT "$2" FOREIGN KEY (mandatoryoptype) REFERENCES obtype(obtypeid);


