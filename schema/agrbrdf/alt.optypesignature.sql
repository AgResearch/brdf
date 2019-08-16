--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY optypesignature
    ADD CONSTRAINT "$1" FOREIGN KEY (obtypeid) REFERENCES obtype(obtypeid);


--
-- Name: $2; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY optypesignature
    ADD CONSTRAINT "$2" FOREIGN KEY (argobtypeid) REFERENCES obtype(obtypeid);


